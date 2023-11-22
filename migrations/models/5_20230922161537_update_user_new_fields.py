from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "full_time_start" DATE;
        ALTER TABLE "users" ADD "demo_status" BOOL NOT NULL  DEFAULT True;
        ALTER TABLE "users" ADD "demo_counter" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "users" ADD "notifi_status" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users" ADD "filters" TEXT;
        ALTER TABLE "users" ADD "full_time_end" DATE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "full_time_start";
        ALTER TABLE "users" DROP COLUMN "demo_status";
        ALTER TABLE "users" DROP COLUMN "demo_counter";
        ALTER TABLE "users" DROP COLUMN "notifi_status";
        ALTER TABLE "users" DROP COLUMN "filters";
        ALTER TABLE "users" DROP COLUMN "full_time_end";"""
