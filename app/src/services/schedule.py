from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.src.services.tracking.mailing import mailing_notices
from app.src.services.tracking.tracking import update_tracks

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


def add_jobs(bot: Bot):
    scheduler.add_job(update_tracks, "cron", hour=7, args=[bot])
    scheduler.add_job(mailing_notices, "cron", hour=9, args=[bot])
