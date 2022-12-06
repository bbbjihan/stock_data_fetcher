import asyncmy


def make_initial(name: str) -> str:
    CHOSUNG_LIST = [
        "ㄱ",
        "ㄲ",
        "ㄴ",
        "ㄷ",
        "ㄸ",
        "ㄹ",
        "ㅁ",
        "ㅂ",
        "ㅃ",
        "ㅅ",
        "ㅆ",
        "ㅇ",
        "ㅈ",
        "ㅉ",
        "ㅊ",
        "ㅋ",
        "ㅌ",
        "ㅍ",
        "ㅎ",
    ]
    chosungs = []
    name = name.replace(" ", "")
    for w in list(name.strip()):
        if "가" <= w <= "힣":
            ch1 = (ord(w) - ord("가")) // 588
            chosungs.append(CHOSUNG_LIST[ch1])
        else:
            chosungs.append(w)
    return "".join(chosungs)


async def tt():
    conn = await asyncmy.connect(
        host="127.0.0.1",
        port=3309,
        user="root",
        password="mysql-db",
        db="finance",
        autocommit=True,
    )
    a = """
    select ISU_CODE, ISU_NAME_SHORT FROM Stock_Info
    """
    async with conn.cursor() as curr:
        await curr.execute(a)
        isu_codes = await curr.fetchall()
    # isu_codes = conn.execute(a).fetchall()
    import itertools

    for isu_code, isu_name_short in itertools.chain(isu_codes):
        # print(make_initial(isu_name_short))
        # continue
        print(isu_code, isu_name_short)

        isu_name_short
        b = f"""
        UPDATE Stock_Info
        SET ISU_NAME_SHORT_INITIAL="{make_initial(isu_name_short)}"
        WHERE ISU_CODE="{isu_code}"
        """
        async with conn.cursor() as curr:
            await curr.execute(b)


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()

    loop.run_until_complete(tt())
