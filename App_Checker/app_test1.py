import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/bootswatch/5.3.0/flatly/bootstrap.min.css",
    {
        "href": "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap",
        "rel": "stylesheet"
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# SAFE INLINE CSS (no html.Style)
hounslow_css = """
body { font-family: 'Roboto', sans-serif; }
.hounslow-header {
    background-color: white;
    border-bottom: 4px solid #4B0055;
    padding: 20px;
    display: flex;
    justify-content: center;
}
.hounslow-title {
    font-size: 28px;
    font-weight: 700;
    color: black;
}
.form-box {
    border: 1px solid #cccccc;
    padding: 25px;
    border-radius: 8px;
    background-color: #ffffff;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.10);
}
.purple-button {
    background-color: #4B0055 !important;
    border-color: #4B0055 !important;
}
.purple-button:hover {
    background-color: #5C2D91 !important;
    border-color: #5C2D91 !important;
}
"""

benefit_options = [
    {"label": "Universal Credit", "value": "Universal Credit"},
    {"label": "Pension Credit", "value": "Pension Credit"},
    {"label": "ESA", "value": "ESA"},
    {"label": "JSA", "value": "JSA"},
    {"label": "Income Support", "value": "Income Support"},
    {"label": "Tax Credits", "value": "Tax Credits"},
]

epc_options = [{"label": r, "value": r} for r in ["A","B","C","D","E","F","G","Unknown"]]

app.layout = html.Div([

    # CORRECT CSS INJECTION (THIS WORKS!)
    html.Meta(charSet="utf-8"),
    html.Style(hounslow_css),

    html.Div([
        html.Div("London Borough of Hounslow", className="hounslow-title")
    ], className="hounslow-header"),

    html.Div([
        html.H2("Energy Support Eligibility Checker", className="text-center mt-4 mb-2"),
        html.P("Enter your details below to check which schemes you may be eligible for.",
               className="text-center mb-4")
    ], className="container"),

    html.Div([
        html.Div([

            html.Div([
                html.Label("Annual Household Income (£)"),
                dcc.Input(id="income", type="text", className="form-control")
            ], className="mb-3"),

            html.Div([
                html.Label("Your Age"),
                dcc.Input(id="age", type="text", className="form-control")
            ], className="mb-3"),

            html.Div([
                html.Label("Benefits Received"),
                dcc.Dropdown(id="benefits", options=benefit_options, multi=True,
                             className="form-control")
            ], className="mb-3"),

            html.Div([
                html.Label("EPC Rating"),
                dcc.Dropdown(id="epc", options=epc_options, className="form-control")
            ], className="mb-3"),

            html.Div([
                html.Label("Energy Debt (£)"),
                dcc.Input(id="debt", type="text", className="form-control")
            ], className="mb-3"),

            html.Div([
                html.Label("Do you own your home?"),
                dcc.RadioItems(id="homeowner",
                               options=[{"label":"Yes","value":"yes"},{"label":"No","value":"no"}],
                               inline=True)
            ], className="mb-3"),

            html.Button("Check Eligibility", id="submit",
                        className="btn btn-primary purple-button"),

            html.Div(id="error", className="text-danger mt-3")

        ], className="col-md-6 mx-auto form-box")
    ], className="container"),

    html.Div([
        html.H3("Results", className="mt-5 mb-3 text-center"),
        html.Div(id="results", className="alert alert-info p-4 shadow-sm")
    ], className="container")
])


@app.callback(
    [Output("results", "children"),
     Output("error", "children")],
    Input("submit", "n_clicks"),
    State("income", "value"),
    State("age", "value"),
    State("benefits", "value"),
    State("epc", "value"),
    State("debt", "value"),
    State("homeowner", "value")
)
def calculate(n, income, age, benefits, epc, debt, homeowner):

    if not n:
        return ("Fill out the form and click 'Check Eligibility'.", "")

    errors = []

    try: income = float(income)
    except: errors.append("Annual income must be a valid number.")

    try: age = int(age)
    except: errors.append("Age must be a valid whole number.")

    try: debt = float(debt)
    except: errors.append("Energy debt must be a valid number.")

    if errors:
        return ("", html.Ul([html.Li(e) for e in errors]))

    benefits = benefits or []
    epc = epc or "Unknown"

    results = {}
    results["Warm Home Discount"] = any(b in benefits for b in [
        "Universal Credit","Pension Credit","ESA","JSA",
        "Income Support","Tax Credits"
    ])
    results["Winter Fuel Payment"] = age >= 66
    results["Great British Insulation Scheme (GBIS)"] = (
        epc in ["D","E","F","G"] or len(benefits) > 0
    )
    results["ECO4"] = (epc in ["D","E","F","G"] and len(benefits) > 0)
    results["Boiler Upgrade Scheme"] = (homeowner == "yes")
    results["Ofgem Debt Relief Scheme"] = (
        debt >= 100 and any(b in benefits for b in [
            "Universal Credit","Pension Credit","ESA","JSA",
            "Income Support","Tax Credits"
        ])
    )

    out = []
    for scheme, ok in results.items():
        out.append(html.Div([
            html.Span("✔ " if ok else "✘ ",
                      style={"color":"green" if ok else "red",
                             "font-weight":"bold","font-size":"18px"}),
            html.Span(f"You are likely eligible for: {scheme}"
                      if ok else f"Likely NOT eligible for: {scheme}")
        ], className="mb-2"))

    return (out, "")


if __name__ == "__main__":
    app.run(debug=True)
