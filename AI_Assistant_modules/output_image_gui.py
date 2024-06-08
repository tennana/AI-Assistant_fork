import gradio as gr

javascript = """
function copyToClipboard() {
    var img = Array.from(document.querySelectorAll('.output-image img') || []).filter(img => img.offsetParent)[0];
    if (!img) {
        return;
    }
    fetch(img.src)
    .then(response => response.blob())
    .then(blob => {
        const item = new ClipboardItem({ "image/png": blob });
        navigator.clipboard.write([item]);
    })
    .catch(console.error);
}
"""

class OutputImage:
    def __init__(self, transfer_target=None):
        self.output_image_path = None
        self.transfer_target = transfer_target

    def layout(self, lang_util):
        output_image = gr.Image(label=lang_util.get_text("output_image"), interactive=False, type="filepath", elem_classes=["output-image"])
        output_image.change(self._set_output_image, inputs=[output_image])
        clipboard_button = gr.Button(""+lang_util.get_text("clipboard"), elem_classes=["clipboard"])
        clipboard_button.click(self._notify, inputs=[output_image], _js=javascript, queue=True)
        if self.transfer_target is not None:
            transfer_button = gr.Button(lang_util.get_text(self.transfer_target.transfer_lang_key))
            transfer_button.click(lambda :self.transfer_target.accept_transfer(self.output_image_path))
        return output_image

    def _set_output_image(self, output_image_path):
        self.output_image_path = output_image_path

    def _notify(self):
        if self.output_image_path is None:
            gr.Warning("Please Image Select")
        else:
            gr.Info("Image Copied to Clipboard")
