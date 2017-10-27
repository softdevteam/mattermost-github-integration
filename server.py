from mattermostgithub import app
try:
    import config
except ImportError:
    from mattermostgithub import config
app.run(
    host=config.SERVER['address'] or "0.0.0.0",
    port=config.SERVER['port'] or 5000,
    debug=False
)
