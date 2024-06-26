import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.img_utils import make_base_pil, base_generation, mask_process
from utils.prompt_utils import remove_duplicates
from utils.request_api import create_and_save_images

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class Img2Img:
    def __init__(self, app_config):
        self.app_config = app_config
        self.input_image = None
        self.output = None

    def layout(self, transfer_target_lang_key=None):
        lang_util = self.app_config.lang_util
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        input_image = gr.Image(label=lang_util.get_text("input_image"), tool="editor", source="upload",
                                               type='filepath', interactive=True)
                    with gr.Column():
                        with gr.Row():
                            mask_image = gr.Image(label=lang_util.get_text("mask_image"), type="pil")
                        with gr.Row():
                            mask_generate_button = gr.Button(lang_util.get_text("create"), interactive=False)
                with gr.Row():
                    [prompt, nega] = PromptAnalysis(self.app_config).layout(lang_util, input_image)
                with gr.Row():
                    fidelity = gr.Slider(minimum=0.0, maximum=0.9, value=0.35, step=0.01, interactive=True,
                                         label=lang_util.get_text("image_fidelity"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"), interactive=False)
            with gr.Column():
                self.output = OutputImage(self.app_config, transfer_target_lang_key)
                output_image = self.output.layout()

        input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[input_image],
                           outputs=[generate_button])
        input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[input_image],
                           outputs=[mask_generate_button])

        mask_generate_button.click(mask_process, inputs=[input_image],
                                   outputs=[mask_image])
        generate_button.click(self._process, inputs=[
            input_image,
            mask_image,
            prompt,
            nega,
            fidelity,
        ], outputs=[output_image])

    def _process(self, input_image_path, mask_image_pil, prompt_text, negative_prompt_text, fidelity):
        prompt = "masterpiece, best quality, " + prompt_text.strip()
        prompt_list = prompt.split(", ")
        # 重複を除去
        unique_tags = remove_duplicates(prompt_list)
        prompt = ", ".join(unique_tags)
        nega = negative_prompt_text.strip()
        base_pil = make_base_pil(input_image_path)
        image_size = base_pil.size
        if mask_image_pil is None:
            mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        else:
            mask_pil = mask_image_pil.resize(base_pil.size, LANCZOS).convert("RGB")
        image_fidelity = 1 - float(fidelity)
        img2img_output_path = self.app_config.make_output_path()
        output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, base_pil, mask_pil,
                                            image_size, img2img_output_path, image_fidelity, self._make_cn_args(), {
                                                "mask": mask_pil,
                                                "mask_blur": 4,
                                                "inpainting_fill": 1,
                                            })
        return output_pil

    def _make_cn_args(self):
        return None
