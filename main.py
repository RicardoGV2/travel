import streamlit as st

# Sample data
data = {
    "12/06": {
        "activity": ["Tour Brisbane", "Story Bridge Adventure Climb"],
        "breakfast": ["The Gunshop Cafe"],
        "lunch": ["Riverbar & Kitchen"],
        "dinner": ["Eagle Street Pier"],
        "transport": ["Uber", "Walk"]
    },
    "13/06": {
        "activity": ["Byron Bay", "Surf Lesson"],
        "breakfast": ["Bayleaf Cafe"],
        "lunch": ["Beach Hotel"],
        "dinner": ["The Balcony Bar & Oyster Co"],
        "transport": ["Car rental"]
    },
    # Add more days as needed
}

st.title("Itinerary Planner")

# Date selection
selected_date = st.selectbox("Select Date:", options=list(data.keys()))

if selected_date:
    # Option Type selection
    option_type = st.selectbox("Option Type:", options=["activity", "breakfast", "lunch", "dinner", "transport"])

    if option_type:
        # Option Value selection
        option_value = st.selectbox("Option Value:", options=data[selected_date][option_type])

        # Display selected option
        if option_value:
            st.write(f"Selected {option_type} for {selected_date}: {option_value}")

            # Display all selected options for the day
            st.write("## Full Itinerary for the day")
            for opt_type, opt_values in data[selected_date].items():
                st.write(f"**{opt_type.capitalize()}:** {', '.join(opt_values)}")

# To run the app, use the command: streamlit run filename.py
