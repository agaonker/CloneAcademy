import streamlit as st
from PIL import Image
import io

# Save the first screenshot
ui_screenshot = Image.open("ui_screenshot.png")
ui_screenshot.save("docs/samples/ui_screenshot.png")

# Save the second screenshot
analysis_output = Image.open("analysis_output.png")
analysis_output.save("docs/samples/analysis_output.png") 