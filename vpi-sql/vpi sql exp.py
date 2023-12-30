import sqlite3

con = sqlite3.connect("vpi.db")
cur = con.cursor()
for i in range(10):
    print("turn ", i)
    for row in list(
        cur.execute("SELECT polity_id, polity_name, polity_desc, creds FROM polities")
    ):
        for row2 in list(
            cur.execute(
                "SELECT system, planet FROM systems WHERE polity_id = ?", (row[0],)
            )
        ):
            for row3 in list(
                cur.execute(
                    "SELECT RO, BP, RS FROM resources WHERE planet = ?", (row2[1],)
                )
            ):
                print("resources stored on planet ", row2[1], ": ", abs(row3[2]))
                """do note resources are stored in NEGATIVE numbers
                  and converted to positive on the point of access
                  idk why i have to do this it breaks otherwise"""
                rsnew = row3[2] + (row3[1] - row3[0])
                cur.execute("DELETE from resources WHERE planet = ?", (row2[1],))
                cur.executemany(
                    "INSERT INTO resources VALUES(?, ?, ?, ?)",
                    [
                        (
                            row2[1],
                            row3[0],
                            row3[1],
                            rsnew,
                        ),
                    ],
                )
                newval = list(
                    cur.execute(
                        "SELECT creds FROM polities WHERE polity_id = ?", (row[0],)
                    )
                )[0][0]
                cur.execute("DELETE from polities WHERE polity_id = ?", (row[0],))
                cur.executemany(
                    "INSERT INTO polities VALUES(?, ?, ?, ?)",
                    [
                        (
                            row[0],
                            row[1],
                            row[2],
                            newval + row3[1],
                        )
                    ],
                )
                con.commit
        print("credits in polity ", row[1], ": ", row[3])
