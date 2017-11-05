from tiny import create_app

if __name__ == "__main__":
    app = create_app("config.Local")
    app.run()
