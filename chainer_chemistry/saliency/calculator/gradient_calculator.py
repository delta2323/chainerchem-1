from chainer_chemistry.saliency.calculator.base_calculator import BaseCalculator  # NOQA


class GradientCalculator(BaseCalculator):

    def __init__(self, model, target_extractor=None, output_extractor=None,
                 eval_fun=None, multiply_target=False, device=None):
        super(GradientCalculator, self).__init__(
            model, target_extractor=target_extractor,
            output_extractor=output_extractor, device=device)
        self.eval_fun = eval_fun or model.__call__
        self.multiply_target = multiply_target

    def _compute_core(self, *inputs):
        self.model.cleargrads()
        outputs = self.eval_fun(*inputs)
        target_var = self.get_target_var(inputs)
        target_var.grad = None  # Need to reset grad beforehand of backward.
        output_var = self.get_output_var(outputs)

        output_var.backward(retain_grad=True)
        saliency = target_var.grad
        if self.multiply_target:
            saliency *= target_var.data
        outputs = (saliency,)
        return outputs
