import aiomysql
from typing import Optional

# 不要忘记配置 DB_CONFIG
from config.main import DB_CONFIG


class AsyncMySQL:
    async def init(self) -> None:
        try:
            self.connection_pool: aiomysql.Pool = await aiomysql.create_pool(
                **DB_CONFIG, autocommit=True, pool_recycle=300
            )
        except Exception as e:
            print("尝试创建连接池时出错: ", e)
            raise e

    async def close(self) -> None:
        self.connection_pool.close()
        await self.connection_pool.wait_closed()
        print("连接池已销毁")

    async def search(
        self,
        column: str,
        table: str,
        cond: str,
        range: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> list:
        try:
            async with self.connection_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    sql = f"SELECT {column} FROM {table} WHERE {cond}\n"
                    if sort:
                        sql += f"ORDER BY {sort}\n"
                    if range:
                        sql += f"LIMIT {range}\n"
                    await cur.execute(sql)

                    return await cur.fetchall()
        except Exception as e:
            print(e)
            return []

    async def insert(self, table: str, column: str, value: str) -> bool:
        try:
            async with self.connection_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    sql = f"INSERT INTO {table}({column}) VALUES({value})\n"
                    await cur.execute(sql)
            return True
        except Exception as e:
            print(e)
            return False

    async def update(self, table: str, updates: str, cond: str) -> bool:
        try:
            async with self.connection_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    sql = f"UPDATE {table} SET {updates} WHERE {cond}\n"
                    await cur.execute(sql)
            return True
        except Exception as e:
            print(e)
            return False

    async def delete(self, table: str, cond: str) -> bool:
        try:
            async with self.connection_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    sql = f"DELETE FROM {table} WHERE {cond}\n"
                    await cur.execute(sql)
            return True
        except Exception as e:
            print(e)
            return False
