from analyzer import run_analysis

# Run the analysis 2 times:
    # Once for topcon, once for trimble

run_analysis({"isTopcon_bool": True}, "TOPCON")

run_analysis({"isTopcon_bool": False}, "TRIMBLE")


# Run the analysis for everything together:

run_analysis({}, "ALL")