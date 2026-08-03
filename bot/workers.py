import asyncio

from database import get_latest_code, remove_code
from api import redeem



async def check_codes():


    while True:


        code = get_latest_code()


        if code:


            # Use dummy validation
            # or an admin account
            response = await redeem(
                "0",
                code,
                "0"
            )


            print(
                code,
                response
            )


            if "expired" in response.lower():

                remove_code(code)


                print(
                    "Removed expired:",
                    code
                )


        await asyncio.sleep(
            3600
        )