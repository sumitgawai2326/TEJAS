import onnx
from onnx import helper, TensorProto
import numpy as np
import cv2
import os

# Create an ONNX model for 10-class classification
# Input: (1, 3, 224, 224)
input_info = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 3, 224, 224])
output_info = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 10])

# GlobalAveragePool: (1, 3, 224, 224) -> (1, 3, 1, 1)
pool_node = helper.make_node('GlobalAveragePool', inputs=['input'], outputs=['pooled'])
# Flatten: (1, 3, 1, 1) -> (1, 3)
flatten_node = helper.make_node('Flatten', inputs=['pooled'], outputs=['flattened'])

# Gemm: (1, 3) x (3, 10) + (10,) -> (1, 10)
np.random.seed(42)
w = np.random.randn(3, 10).astype(np.float32)
b = np.zeros(10, dtype=np.float32)
w_init = helper.make_tensor('w', TensorProto.FLOAT, [3, 10], w.flatten().tolist())
b_init = helper.make_tensor('b', TensorProto.FLOAT, [10], b.flatten().tolist())

gemm_node = helper.make_node('Gemm', inputs=['flattened', 'w', 'b'], outputs=['output'], alpha=1.0, beta=1.0)

graph = helper.make_graph(
    [pool_node, flatten_node, gemm_node],
    'krishidrishti_tomato_cls',
    [input_info],
    [output_info],
    [w_init, b_init]
)
model = helper.make_model(graph, producer_name='KrishiDrishti', opset_imports=[helper.make_opsetid('', 14)])
onnx.checker.check_model(model)
onnx.save(model, 'test_model.onnx')
print('ONNX model saved successfully.')

# Test inference with OpenCV DNN
net = cv2.dnn.readNetFromONNX('test_model.onnx')
blob = np.random.randn(1, 3, 224, 224).astype(np.float32)
net.setInput(blob)
out = net.forward()
print('OpenCV DNN output shape:', out.shape)
print('OpenCV DNN output values:', out)

# Clean up
if os.path.exists('test_model.onnx'):
    os.remove('test_model.onnx')
print('DONE!')
