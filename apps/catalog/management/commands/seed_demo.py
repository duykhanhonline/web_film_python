"""Demo data for local development. Placeholder gradient images only, never real artwork."""

import io
import json
import re
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from PIL import Image

from apps.ads.models import AdSlot, Creative, SponsoredRow
from apps.billing.models import Plan, Subscription
from apps.catalog.models import Banner, Country, Episode, Genre, Movie, Season
from apps.catalog.text import slugify_vi
from apps.player.models import WatchProgress

DATA = Path(__file__).parent / "seed_data" / "movies.json"

COUNTRIES = ["Hàn Quốc", "Trung Quốc", "Việt Nam", "Thái Lan", "Nhật Bản", "Âu Mỹ"]
TOP10 = [
    "truong-ca-phuong-hoang",
    "mua-he-cuoi-cung",
    "hau-due-mat-troi",
    "nha-co-ba-chi-em",
    "ma-lang",
    "dau-bep-nha-ben",
    "nhiem-vu-cuoi-cung",
    "hoc-vien-phap-su",
    "kiem-tam-truyen-ky",
    "chuyen-xe-cuoi-ngay",
]
HERO = [
    "truong-ca-phuong-hoang",
    "mua-he-cuoi-cung",
    None,
    "nhiem-vu-cuoi-cung",
    "nha-co-ba-chi-em",
]
SPONSORED = [
    "bangkok-ve-dem",
    "hen-em-o-da-lat",
    "tinh-yeu-mua-mua",
    "rong-thep",
    "thanh-pho-khong-ngu",
    "dau-bep-nha-ben",
]
# (slug, episode number or None for movies, watched seconds)
CONTINUE = [
    ("hau-due-mat-troi", 9, 1830),
    ("nhiem-vu-cuoi-cung", None, 4210),
    ("truong-ca-phuong-hoang", 21, 600),
    ("hoc-vien-phap-su", 4, 900),
]
PLANS = [
    ("Gói 1 tháng", 1, 99_000, False),
    ("Gói 3 tháng", 3, 269_000, False),
    ("Gói 12 tháng", 12, 899_000, True),
]
AD_COLOR = "3A3322"
DEMO_PASSWORD = "demo12345"
EPISODE_SECONDS = 45 * 60


def gradient(color: str, size: tuple[int, int]) -> ContentFile:
    """A vertical gradient from `color` to near-black, as WebP."""
    top = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
    bottom = tuple(max(0, c // 4) for c in top)
    column = Image.new("RGB", (1, 256))
    for y in range(256):
        t = y / 255
        column.putpixel(
            (0, y), tuple(round(a + (b - a) * t) for a, b in zip(top, bottom, strict=True))
        )
    img = column.resize(size, Image.Resampling.BILINEAR)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=80)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu: phim, banner, gói VIP, quảng cáo, tài khoản demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true", help="Xóa dữ liệu phim/quảng cáo cũ trước khi tạo."
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo chỉ chạy khi DEBUG=True.")
        if options["flush"]:
            self.flush()
        elif Movie.objects.exists():
            raise CommandError("Đã có dữ liệu phim. Chạy lại với --flush để tạo mới.")

        with transaction.atomic():
            movies = self.seed_movies()
            self.seed_banners(movies)
            self.seed_plans()
            self.seed_ads(movies)
            self.seed_users(movies)
        cache.clear()
        self.stdout.write(self.style.SUCCESS(f"Đã tạo {len(movies)} phim mẫu."))
        self.stdout.write(
            f"Tài khoản demo (đăng nhập qua /admin/): demo / {DEMO_PASSWORD} (miễn phí), "
            f"demovip / {DEMO_PASSWORD} (VIP)"
        )

    def flush(self) -> None:
        for model in (Banner, Movie, Country, Genre, Creative, AdSlot, SponsoredRow):
            model.objects.all().delete()
        Subscription.objects.all().delete()
        Plan.objects.all().delete()

    def seed_movies(self) -> dict[str, Movie]:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        countries = {
            name: Country.objects.create(name=name, slug=slugify_vi(name), order=i)
            for i, name in enumerate(COUNTRIES)
        }
        genre_names = sorted({g for item in data for g in item["genres"]})
        genres = {
            name: Genre.objects.create(name=name, slug=slugify_vi(name)) for name in genre_names
        }

        now = timezone.now()
        movies = {}
        for i, item in enumerate(data):
            color = re.search(r"/([0-9A-Fa-f]{6})/", item["poster"]).group(1)
            views = (len(TOP10) - TOP10.index(item["id"])) * 1000 if item["id"] in TOP10 else i
            movie = Movie(
                title=item["title"],
                original_title=item["originalTitle"],
                slug=item["id"],
                kind=item["type"],
                country=countries[item["country"]],
                year=item["year"],
                age_rating=item["ageRating"],
                has_vietsub="Vietsub" in item["audio"],
                has_thuyet_minh="Thuyết minh" in item["audio"],
                has_long_tieng="Lồng tiếng" in item["audio"],
                access=item["access"],
                synopsis=item["synopsis"],
                duration_minutes=item.get("duration"),
                total_episodes=(item.get("episodes") or {}).get("total"),
                schedule_text=item.get("schedule") or "",
                view_count=views,
            )
            movie.poster.save(f"{item['id']}.webp", gradient(color, (400, 600)), save=False)
            movie.backdrop.save(f"{item['id']}.webp", gradient(color, (1920, 1080)), save=False)
            movie.save()
            movie.genres.set(genres[g] for g in item["genres"])

            season = Season.objects.create(movie=movie, number=1)
            if item["type"] == Movie.Kind.SERIES:
                count = item["episodes"]["current"]
                # New titles got their latest episode yesterday; others a month ago
                latest = now - timedelta(days=1 if item["isNew"] else 30)
                Episode.objects.bulk_create(
                    Episode(
                        season=season,
                        number=n,
                        duration=EPISODE_SECONDS,
                        intro_end=90,
                        published_at=latest - timedelta(days=7 * (count - n)),
                    )
                    for n in range(1, count + 1)
                )
            else:
                Episode.objects.create(
                    season=season,
                    number=1,
                    duration=item["duration"] * 60,
                    intro_end=0,
                    published_at=now - timedelta(days=2 if item["isNew"] else 90),
                )
            movies[item["id"]] = movie
        return movies

    def seed_banners(self, movies: dict[str, Movie]) -> None:
        for order, slug in enumerate(HERO):
            if slug:
                Banner.objects.create(movie=movies[slug], order=order)
                continue
            banner = Banner(
                title="Mùa hè rực rỡ cùng nhà tài trợ",
                synopsis="Nội dung quảng cáo mẫu cho vị trí slide tài trợ.",
                sponsor_name="Thương hiệu tài trợ",
                link="https://example.com/",
                order=order,
            )
            banner.image.save("sponsored.webp", gradient(AD_COLOR, (1920, 1080)), save=False)
            banner.save()

    def seed_plans(self) -> None:
        for name, months, price, best in PLANS:
            Plan.objects.create(name=name, months=months, price_vnd=price, is_best_value=best)

    def seed_ads(self, movies: dict[str, Movie]) -> None:
        slots = {code: AdSlot.objects.create(code=code) for code in AdSlot.Code.values}
        # ad-infeed has no creative on purpose, so the house ad shows there
        for code, desktop, mobile in [
            ("ad-billboard", (970, 250), (320, 100)),
            ("ad-sidebar", (300, 250), (300, 250)),
        ]:
            creative = Creative(
                slot=slots[code],
                name=f"Mẫu {code}",
                link="https://example.com/",
                alt_text="Quảng cáo mẫu",
            )
            creative.image_desktop.save(
                f"{code}-desktop.webp", gradient(AD_COLOR, desktop), save=False
            )
            creative.image_mobile.save(
                f"{code}-mobile.webp", gradient(AD_COLOR, mobile), save=False
            )
            creative.save()

        row = SponsoredRow.objects.create(
            title="Phim hè sôi động", sponsor_name="Thương hiệu tài trợ"
        )
        row.movies.set(movies[slug] for slug in SPONSORED)

    def seed_users(self, movies: dict[str, Movie]) -> None:
        User = get_user_model()
        demo, _ = User.objects.get_or_create(username="demo", defaults={"is_staff": True})
        vip, _ = User.objects.get_or_create(username="demovip", defaults={"is_staff": True})
        for user in (demo, vip):
            user.set_password(DEMO_PASSWORD)
            user.save()

        now = timezone.now()
        Subscription.objects.create(
            user=vip,
            plan=Plan.objects.get(months=1),
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=29),
        )

        WatchProgress.objects.filter(user__in=[demo, vip]).delete()
        for slug, number, watched in CONTINUE:
            episode = Episode.objects.get(season__movie=movies[slug], number=number or 1)
            for user in (demo, vip):
                WatchProgress.objects.create(user=user, episode=episode, position_seconds=watched)
