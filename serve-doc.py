from livereload import Server, shell

app = Server()
app.watch("docs", shell("make docs"), delay=2)
app.serve(root="docs/_build/html/")
