import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.application import make_output_path
from utils.img_utils import base_generation, canny_process, resize_image_aspect_ratio, invert_process
from utils.prompt_utils import prepare_prompt
from utils.request_api import create_and_save_images

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class NormalMap:
    def __init__(self, app_config):
        self.app_config = app_config
        self.input_image = None
        self.output = None

    def layout(self, lang_util, transfer_target_lang_key=None):
        with gr.Row() as self.block:
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        self.input_image = gr.Image(label=lang_util.get_text("input_image"), tool="editor",
                                                    source="upload",
                                                    type='filepath', interactive=True)
                    with gr.Column():
                        pass
                with gr.Row():
                    [prompt, nega] = PromptAnalysis().layout(lang_util, self.input_image)
                with gr.Row():
                    fidelity = gr.Slider(minimum=0.75, maximum=1.5, value=1.0, step=0.01, interactive=True,
                                         label=lang_util.get_text("lineart_fidelity"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"))
            with gr.Column():
                self.output = OutputImage(transfer_target_lang_key)
                output_image = self.output.layout(lang_util)

        generate_button.click(self._process, inputs=[
            self.input_image,
            prompt,
            nega,
            fidelity,
        ], outputs=[output_image])

    def _process(self, input_image_path, prompt_text, negative_prompt_text, fidelity):
        prompt = "masterpiece, best quality, normal map, <lora:sdxl-testlora-normalmap_04b_dim32:1.2>" + prompt_text.strip()
        execute_tags = ["monochrome", "greyscale", "lineart", "white background", "sketch"]
        prompt = prepare_prompt(execute_tags, prompt)
        nega = negative_prompt_text.strip()
        base_pil = Image.open(input_image_path).convert("RGBA")
        image_size = base_pil.size
        base_pil = resize_image_aspect_ratio(base_pil)
        base_pil = base_generation(base_pil.size, (150, 110, 255, 255)).convert("RGB")
        invert_pil = invert_process(input_image_path).resize(base_pil.size, LANCZOS).convert("RGB")
        mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        image_fidelity = 1.0
        lineart_fidelity = float(fidelity)
        normalmap_output_path = make_output_path(self.app_config.dpath)
        mode = "normalmap"
        output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, base_pil, invert_pil, mask_pil,
                                            image_size, normalmap_output_path, mode, image_fidelity, lineart_fidelity)
        return output_pil

    def _make_canny(self, canny_img_path, canny_threshold1, canny_threshold2):
        threshold1 = int(canny_threshold1)
        threshold2 = int(canny_threshold2)
        return canny_process(canny_img_path, threshold1, threshold2)