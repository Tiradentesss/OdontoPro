from config.database import get_connection


def main():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT VERSION()")
    ver = cur.fetchone()[0]
    print(ver)
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
