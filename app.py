  import streamlit as st
  import pandas as pd
  import numpy as np
  from datetime import datetime

  # ----------------------------------------------------------------
  # 2. DATABASE & CONFIGURATION
  # ----------------------------------------------------------------
  # Define a dictionary for common steel sections (kg/m, Surface m2/m)
  SECTION_DB = {
      "IPE 100": {"kg_per_m": 9.42, "paint_area": 0.08},
      "IPE 140": {"kg_per_m": 11.48, "paint_area": 0.12},
      "IPE 200": {"kg_per_m": 17.69, "paint_area": 0.19},
      "H 200x100x6x8": {"kg_per_m": 16.0, "paint_area": 0.18},
      "H 300x150x6x9": {"kg_per_m": 25.0, "paint_area": 0.28},
      "C 150": {"kg_per_m": 12.0, "paint_area": 0.15},
      "Custom / Other": {"kg_per_m": 0.0, "paint_area": 0.0}
  }

  # Session State Initialization
  # This allows us to store the DataFrame between app reruns
  if 'steel_df' not in st.session_state:
      # Initial empty DataFrame
      st.session_state['steel_df'] = pd.DataFrame(columns=[
          'Section', 'Quantity', 'Length', 'Rate/kg', 'Rate/m2',
          'Weight', 'Surface', 'Total_Steel', 'Total_Paint', 'Total_Cost', 'Date'
      ])

  # ----------------------------------------------------------------
  # 3. SIDEBAR: SETTINGS & RATES
  # ----------------------------------------------------------------
  with st.sidebar:
      st.title("📊 Settings")

      st.markdown("**Global Material Rates**")

      # Get current rates, or use defaults if not in state
      if 'rate_kg' not in st.session_state: st.session_state['rate_kg'] = 65.0 # THB/kg
      if 'rate_paint' not in st.session_state: st.session_state['rate_paint'] = 45.0 # THB/m2

      rate_kg = st.number_input(
          "Steel Rate (THB/kg)",
          value=st.session_state['rate_kg'],
          min_value=0.0,
          format="%.2f"
      )
      rate_paint = st.number_input(
          "Paint Rate (THB/m2)",
          value=st.session_state['rate_paint'],
          min_value=0.0,
          format="%.2f"
      )

      st.session_state['rate_kg'] = rate_kg
      st.session_state['rate_paint'] = rate_paint

      st.info("💡 Tip: You can change the rates at any time to see new total costs instantly.")

  # ----------------------------------------------------------------
  # 4. INPUT SECTION: ADD ROWS
  # ----------------------------------------------------------------
  col1, col2 = st.columns(2)

  with col1:
      st.markdown("**1. Section Details**")
      st.markdown("_Select from DB or use a custom section._")

      # Populate Selectbox based on Database
      options = list(SECTION_DB.keys()) + ['Custom / Other']
      selected_section = st.selectbox("Steel Section", options, index=0)

      # If 'Custom' or 'Other', allow manual input
      if selected_section in ['Custom / Other', '']:
          st.warning("Please enter custom values below.")
          weight_prop = st.number_input("Custom Weight (kg/m)", value=0.0, format="%.2f")
          surface_prop = st.number_input("Custom Surface (m2/m)", value=0.0, format="%.2f")
      else:
          # Use DB values
          weight_prop, surface_prop = SECTION_DB[selected_section]['kg_per_m'],
  SECTION_DB[selected_section]['paint_area']
          st.write(f"**Weight:** {weight_prop} kg/m | **Paint Area:** {surface_prop} m²/m")

      # Quantity & Length
      qty = st.number_input("Quantity (Sets/pcs)", value=1, min_value=0, format="%d")
      length = st.number_input("Length (m)", value=1.0, min_value=0.0, format="%.2f")

  with col2:
      st.markdown("**2. Actions**")

      if st.button("➕ Add Row", use_container_width=True):
          # Prepare new row data
          new_row = pd.Series([
              selected_section,
              qty,
              length,
              rate_kg, # Store the current rate at time of add
              rate_paint,
              0.0, # Weight (will be calculated)
              0.0, # Surface (will be calculated)
              0.0, # Total Steel (will be calculated)
              0.0, # Total Paint (will be calculated)
              0.0, # Total Cost (will be calculated)
              datetime.now().strftime("%Y-%m-%d") # Default Date
          ], index=['Section', 'Quantity', 'Length', 'Rate/kg', 'Rate/m2',
                    'Weight', 'Surface', 'Total_Steel', 'Total_Paint', 'Total_Cost', 'Date'])

          # Append to session state
          st.session_state['steel_df'] = pd.concat([st.session_state['steel_df'], new_row])
          st.rerun() # Trigger a rerun to update the UI with the new row

  # ----------------------------------------------------------------
  # 5. CALCULATION LOGIC
  # ----------------------------------------------------------------
  def calculate_row(row, rate_kg, rate_paint, section_name):
      # Logic to calculate values for a single row

      # Retrieve properties for the section
      if section_name in SECTION_DB:
          weight_prop, surface_prop = SECTION_DB[section_name]
      else:
          # If user selected Custom or empty
          weight_prop, surface_prop = row['Custom Weight (kg/m)'], row['Custom Surface (m2/m)']

      qty = row['Quantity']
      length = row['Length']

      # Calculate Metrics
      if qty > 0 and length > 0:
          calc_total_weight = qty * length * weight_prop
          calc_total_surface = calc_total_weight / weight_prop * surface_prop
          calc_total_cost = (calc_total_weight * rate_kg) + (calc_total_surface * rate_paint)

          row['Weight'] = calc_total_weight
          row['Surface'] = calc_total_surface
          row['Total_Steel'] = calc_total_weight * rate_kg
          row['Total_Paint'] = calc_total_surface * rate_paint
          row['Total_Cost'] = calc_total_cost
      else:
          # If inputs are 0, keep calculated values as 0
          row['Weight'] = 0
          row['Surface'] = 0
          row['Total_Steel'] = 0
          row['Total_Paint'] = 0
          row['Total_Cost'] = 0

      return row

  # ----------------------------------------------------------------
  # 6. DISPLAY RESULTS (TABLE)
  # ----------------------------------------------------------------
  if 'steel_df' not in st.session_state:
      st.write("⚠️ **No data entered yet.** Add steel sections in the left column.")

  else:
      st.markdown("---")
      st.header("📋 Bill of Materials (BOM) & Cost Estimate")

      # Apply calculations to every row
      # We create a list to hold the processed rows to update the DataFrame
      rows_to_calc = []
      for index, row in st.session_state['steel_df'].iterrows():
          # Get current rates from session state (might have changed)
          curr_kg = st.session_state['rate_kg']
          curr_paint = st.session_state['rate_paint']

          # Recalculate the row with current rates
          # Note: We need to handle 'Custom' logic inside the loop
          sec = row['Section']
          if sec in SECTION_DB:
              w, s = SECTION_DB[sec]
          else:
              w, s = row.get('Weight', 0), row.get('Surface', 0) # Simplified for custom logic

          if w == 0 and s == 0:
               # Fallback if Custom logic failed
               rows_to_calc.append(row)
          else:
               # Standard calculation
               qty = row['Quantity']
               length = row['Length']

               if qty > 0 and length > 0:
                   calc_weight = qty * length * w
                   calc_surface = calc_weight / w * s
                   calc_cost = (calc_weight * curr_kg) + (calc_surface * curr_paint)

                   # Create a new series with updated values
                   updated_row = row.copy()
                   updated_row['Weight'] = calc_weight
                   updated_row['Surface'] = calc_surface
                   updated_row['Total_Steel'] = calc_weight * curr_kg
                   updated_row['Total_Paint'] = calc_surface * curr_paint
                   updated_row['Total_Cost'] = calc_cost
                   rows_to_calc.append(updated_row)
               else:
                   rows_to_calc.append(row)

      st.session_state['steel_df'] = pd.DataFrame(rows_to_calc)

      # Render the DataFrame directly
      st.dataframe(st.session_state['steel_df'], use_container_width=True, hide_index=True)

      # Calculate Grand Totals
      total_weight = st.session_state['steel_df']['Weight'].sum()
      total_surface = st.session_state['steel_df']['Surface'].sum()
      total_cost = st.session_state['steel_df']['Total_Cost'].sum()

      # Display summary metrics
      col1, col2, col3 = st.columns(3)

      with col1:
          st.metric(label="Total Weight", value=f"{total_weight:.2f} kg", delta=f"{total_weight:.2f} kg")
      with col2:
          st.metric(label="Total Surface", value=f"{total_surface:.2f} m²", delta=f"{total_surface:.2f} m²")
      with col3:
          st.metric(label="Total Estimated Cost", value=f"{total_cost:.2f} THB", delta=f"{total_cost:.2f} THB")

      # Export Button
      csv_data = st.session_state['steel_df'].to_csv(index=False).encode('utf-8')
      st.download_button(
          label="💾 Download CSV",
          data=csv_data,
          file_name="steel_takeoff.csv",
          mime="text/csv"
      )