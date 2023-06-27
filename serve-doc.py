from livereload import Server, shell

app = Server()
app.watch("docs", shell("make build-docs"), delay=2)
app.serve(root="build/_html/")
