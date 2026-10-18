"""Run: python app.py [--offline] [--share]."""
import argparse
import os
from agent import build_ui

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cedar & Circuit business assistant")
    parser.add_argument("--offline", action="store_true", help="Explicit scripted test fixture; makes no API calls")
    parser.add_argument("--share", action="store_true", help="Create a temporary public Gradio URL")
    args = parser.parse_args()
    build_ui(offline=args.offline).launch(server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
                                        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")), share=args.share)
