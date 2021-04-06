from app import app
import index

app.layout = index.layout
app.config.suppress_callback_exceptions = True
app.title = 'Greenfield Optimization v0.1'

if __name__ == "__main__":
    app.run_server(port=8880, debug=True)