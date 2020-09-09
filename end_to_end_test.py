from src.server import Server


Server(name=str("Kermit"), port=int(10010)).start()
Server(name=str("MsPiggy"), port=int(10011)).start()
Server(name=str("Gonzo"), port=int(10012)).start()
Server(name=str("Beaker"), port=int(10013)).start()
Server(name=str("Fozzie"), port=int(10014)).start()

