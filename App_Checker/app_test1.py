import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/bootswatch/5.3.0/flatly/bootstrap.min.css"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

benefit_options = [
    {"label": "Universal Credit", "value": "Universal Credit"},
    {"label": "Pension Credit", "value": "Pension Credit"},
    {"label": "ESA", "value": "ESA"},
    {"label": "JSA", "value": "JSA"},
    {"label": "Income Support", "value": "Income Support"},
    {"label": "Tax Credits", "value": "Tax Credits"},
]

epc_options = [{"label": r, "value": r} for r in ["A", "B", "C", "D", "E", "F", "G", "Unknown"]]

app.layout = html.Div([
    html.Div([
        html.H2("The London Borough of Hounslow Energy Support Eligibility Checker", className="text-center mt-4 mb-4"),
        html.P("Enter your details below to check which schemes you may be eligible for.",
               className="text-center")
    ], className="container"),

    html.Div([
    html.Div([
        html.Label("Annual Household Income (£) - no commas or spaces"),
        dcc.Input(id="income", type="text", className="form-control", inputMode="numeric")
    ], className="mb-3"),

    html.Div([
        html.Label("Your Age"),
        dcc.Input(id="age", type="text", className="form-control", inputMode="numeric")
    ], className="mb-3"),

    html.Div([
        html.Label("Benefits Received"),
        dcc.Dropdown(id="benefits", options=benefit_options, multi=True, className="form-control")
    ], className="mb-3"),

    html.Div([
        html.Label("EPC Rating"),
        dcc.Dropdown(id="epc", options=epc_options, className="form-control")
    ], className="mb-3"),

    html.Div([
        html.Label("Energy Debt (£)"),
        dcc.Input(id="debt", type="text", className="form-control", inputMode="numeric")
    ], className="mb-3"),

    html.Div([
        html.Label("Do you own your home?"),
        dcc.RadioItems(
            id="homeowner",
            options=[{"label": "Yes", "value": "yes"}, {"label": "No", "value": "no"}],
            inline=True
        )
    ], className="mb-3"),

    html.Button("Check Eligibility", id="submit", className="btn btn-primary mt-3"),

    html.Div(id="error", className="text-danger mt-3")

], className="col-md-6 mx-auto")
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

    # -------------------- VALIDATION --------------------
    errors = []

    # Convert numeric fields safely
    try:
        income = float(income)
    except:
        errors.append("Annual income must be a valid number.")

    try:
        age = int(age)
    except:
        errors.append("Age must be a valid whole number.")

    try:
        debt = float(debt)
    except:
        errors.append("Energy debt must be a valid number.")

    if errors:
        return ("", html.Ul([html.Li(e) for e in errors]))

    benefits = benefits or []
    epc = epc or "Unknown"

    # -------------------- ELIGIBILITY RULES --------------------
    results = {}

    results["Warm Home Discount"] = any(b in benefits for b in [
        "Universal Credit", "Pension Credit", "ESA", "JSA",
        "Income Support", "Tax Credits"
    ])

    results["Winter Fuel Payment"] = age >= 66

    results["Great British Insulation Scheme (GBIS)"] = (
        epc in ["D", "E", "F", "G"] or len(benefits) > 0
    )

    results["ECO4"] = (
        epc in ["D", "E", "F", "G"] and len(benefits) > 0
    )

    results["Boiler Upgrade Scheme"] = (homeowner == "yes")

    results["Ofgem Debt Relief Scheme"] = (
        debt >= 100 and any(
            b in benefits for b in [
                "Universal Credit", "Pension Credit", "ESA", "JSA",
                "Income Support", "Tax Credits"
            ]
        )
    )

    # -------------------- BUILD RESULT UI --------------------
    output = []
    for scheme, ok in results.items():
        if ok:
            output.append(html.Div([
                html.Span("✔ ", style={"color": "green", "font-weight": "bold", "font-size": "18px"}),
                html.Span(f"You are likely eligible for: {scheme}")
            ], className="mb-2"))
        else:
            output.append(html.Div([
                html.Span("✘ ", style={"color": "red", "font-weight": "bold", "font-size": "18px"}),
                html.Span(f"Likely NOT eligible for: {scheme}")
            ], className="mb-2"))

    return (output, "")


if __name__ == "__main__":
    app.run(debug=True)