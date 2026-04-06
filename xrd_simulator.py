import math
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


# =========================
# CALCULATIONS
# =========================

def compute_two_probe(I, V, L, A, R_contact=0, R_wires=0):
    if I == 0:
        return None, None

    R_measured = V / I
    R_sample = R_measured - (2 * R_contact + R_wires)
    rho = R_sample * (A / L)

    return R_sample, rho


def compute_four_probe(I, V, s, t=None):
    if I == 0:
        return None

    if t is None:
        # Bulk
        rho = 2 * math.pi * s * (V / I)
    else:
        # Thin film
        rho = (math.pi / math.log(2)) * t * (V / I)

    return rho


# =========================
# GRAPH
# =========================

def plot_vi_graph(currents, voltages):
    fig, ax = plt.subplots()

    ax.plot(currents, voltages, 'o-', label="Experimental Data")
    
    # Linear fit
    coeffs = np.polyfit(currents, voltages, 1)
    fit_line = np.poly1d(coeffs)
    ax.plot(currents, fit_line(currents), '--', label=f"Slope (R) = {coeffs[0]:.2f} Ω")

    ax.set_xlabel("Current (A)")
    ax.set_ylabel("Voltage (V)")
    ax.set_title("V vs I Graph")
    ax.legend()
    ax.grid()

    return fig, coeffs[0]


# =========================
# DIAGRAMS
# =========================

def draw_two_probe():
    fig, ax = plt.subplots()

    # Sample
    ax.add_patch(plt.Rectangle((0, 0), 6, 1, color='lightgray'))

    # Probes
    ax.plot([1, 1], [1, 2], 'k', lw=2)
    ax.plot([5, 5], [1, 2], 'k', lw=2)

    # Labels
    ax.text(1, 2.2, "I & V", ha='center')
    ax.text(5, 2.2, "I & V", ha='center')
    ax.text(2.5, -0.5, "Sample", fontsize=10)

    ax.set_xlim(-1, 7)
    ax.set_ylim(-1, 3)
    ax.axis('off')

    return fig


def draw_four_probe():
    fig, ax = plt.subplots()

    # Sample
    ax.add_patch(plt.Rectangle((0, 0), 6, 1, color='lightgray'))

    # Probes
    x_positions = [1, 2.5, 3.5, 5]
    labels = ["I+", "V", "V", "I-"]

    for x, label in zip(x_positions, labels):
        ax.plot([x, x], [1, 2], 'k', lw=2)
        ax.text(x, 2.2, label, ha='center')

    ax.text(2.5, -0.5, "Sample", fontsize=10)

    ax.set_xlim(-1, 7)
    ax.set_ylim(-1, 3)
    ax.axis('off')

    return fig


# =========================
# MAIN APP
# =========================

def main():
    st.set_page_config(page_title="Probe Method Simulator", layout="centered")

    st.title("Two-Probe & Four-Probe Resistivity Simulator")

    st.sidebar.header("Inputs")

    method = st.sidebar.selectbox("Select Method", ["Two-Probe", "Four-Probe"])

    I = st.sidebar.number_input("Current (A)", value=1.0)
    V = st.sidebar.number_input("Voltage (V)", value=2.0)

    st.sidebar.subheader("Sample Parameters")
    L = st.sidebar.number_input("Length (m)", value=0.5)
    A = st.sidebar.number_input("Area (m²)", value=1e-6)

    currents = st.sidebar.text_input("Currents (comma separated)", "1,2,3,4,5")
    voltages = st.sidebar.text_input("Voltages (comma separated)", "2,4,6,8,10")

    try:
        currents = np.array([float(i) for i in currents.split(",")])
        voltages = np.array([float(v) for v in voltages.split(",")])
    except:
        st.error("Invalid data format")
        return

    st.subheader("Results")

    if method == "Two-Probe":
        R_contact = st.sidebar.number_input("Contact Resistance (Ω)", value=0.5)
        R_wires = st.sidebar.number_input("Wire Resistance (Ω)", value=0.2)

        R, rho = compute_two_probe(I, V, L, A, R_contact, R_wires)

        st.metric("Sample Resistance (Ω)", f"{R:.3f}")
        st.metric("Resistivity (Ω·m)", f"{rho:.3e}")

        st.latex(r"R_{total} = R_{sample} + 2R_{contact} + R_{wires}")
        st.latex(r"\rho = R \frac{A}{L}")

        st.pyplot(draw_two_probe())

    else:
        s = st.sidebar.number_input("Probe Spacing (m)", value=0.002)
        thin = st.sidebar.checkbox("Thin Film")

        if thin:
            t = st.sidebar.number_input("Thickness (m)", value=1e-6)
            rho = compute_four_probe(I, V, s, t)
            st.latex(r"\rho = \frac{\pi}{\ln(2)} t \frac{V}{I}")
        else:
            rho = compute_four_probe(I, V, s)
            st.latex(r"\rho = 2\pi s \frac{V}{I}")

        st.metric("Resistivity (Ω·m)", f"{rho:.3e}")

        st.pyplot(draw_four_probe())

    st.subheader("V vs I Graph")
    fig, slope = plot_vi_graph(currents, voltages)
    st.pyplot(fig)

    st.metric("Slope (Resistance Ω)", f"{slope:.2f}")

    st.info("Four-Probe method eliminates contact resistance, making it more accurate.")

# =========================

if __name__ == "__main__":
    main()