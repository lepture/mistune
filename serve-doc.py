from livereload import Server, shell

app = Server()
app.watch("docs/*.rst", shell("make docs"), delay=2)
app.serve(root="docs/_build/html/")
