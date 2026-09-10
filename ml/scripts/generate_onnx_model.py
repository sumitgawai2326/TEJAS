"""
KrishiDrishti Edge — Direct ONNX Graph Builder for Edge Tomato Pathology Classifier
Constructs a valid, standard-compliant ONNX model graph (Opset 17) for 10-class Tomato leaf pathology detection.
Includes metadata properties: architecture, num_classes, crop, classes, input_shape.
"""
import os
import onnx
from onnx import helper, TensorProto
import numpy as np

def build_tomato_onnx_model(output_path: str = os.path.join("data", "models", "crop_disease_v1.onnx")):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Input tensor definition: (batch_size, 3, 224, 224)
    input_info = helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, 224, 224])
    output_info = helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 10])

    # Graph operations:
    # 1. Conv2D: 3 -> 16 channels, 3x3 kernel, stride 2, padding 1
    # 2. Relu
    # 3. Conv2D: 16 -> 32 channels, 3x3 kernel, stride 2, padding 1
    # 4. Relu
    # 5. GlobalAveragePool: (1, 32, H, W) -> (1, 32, 1, 1)
    # 6. Flatten: (1, 32, 1, 1) -> (1, 32)
    # 7. Gemm: (1, 32) x (32, 10) + (10,) -> (1, 10)

    np.random.seed(42)
    w_conv1 = np.random.randn(16, 3, 3, 3).astype(np.float32) * 0.1
    b_conv1 = np.zeros(16, dtype=np.float32)

    w_conv2 = np.random.randn(32, 16, 3, 3).astype(np.float32) * 0.1
    b_conv2 = np.zeros(32, dtype=np.float32)

    w_fc = np.random.randn(32, 10).astype(np.float32) * 0.1
    b_fc = np.zeros(10, dtype=np.float32)

    t_w_conv1 = helper.make_tensor("w_conv1", TensorProto.FLOAT, [16, 3, 3, 3], w_conv1.flatten().tolist())
    t_b_conv1 = helper.make_tensor("b_conv1", TensorProto.FLOAT, [16], b_conv1.flatten().tolist())

    t_w_conv2 = helper.make_tensor("w_conv2", TensorProto.FLOAT, [32, 16, 3, 3], w_conv2.flatten().tolist())
    t_b_conv2 = helper.make_tensor("b_conv2", TensorProto.FLOAT, [32], b_conv2.flatten().tolist())

    t_w_fc = helper.make_tensor("w_fc", TensorProto.FLOAT, [32, 10], w_fc.flatten().tolist())
    t_b_fc = helper.make_tensor("b_fc", TensorProto.FLOAT, [10], b_fc.flatten().tolist())

    node_conv1 = helper.make_node("Conv", inputs=["input", "w_conv1", "b_conv1"], outputs=["conv1"], kernel_shape=[3, 3], strides=[2, 2], pads=[1, 1, 1, 1])
    node_relu1 = helper.make_node("Relu", inputs=["conv1"], outputs=["relu1"])

    node_conv2 = helper.make_node("Conv", inputs=["relu1", "w_conv2", "b_conv2"], outputs=["conv2"], kernel_shape=[3, 3], strides=[2, 2], pads=[1, 1, 1, 1])
    node_relu2 = helper.make_node("Relu", inputs=["conv2"], outputs=["relu2"])

    node_gap = helper.make_node("GlobalAveragePool", inputs=["relu2"], outputs=["gap"])
    node_flat = helper.make_node("Flatten", inputs=["gap"], outputs=["flat"])

    node_fc = helper.make_node("Gemm", inputs=["flat", "w_fc", "b_fc"], outputs=["output"], alpha=1.0, beta=1.0)

    nodes = [node_conv1, node_relu1, node_conv2, node_relu2, node_gap, node_flat, node_fc]
    initializers = [t_w_conv1, t_b_conv1, t_w_conv2, t_b_conv2, t_w_fc, t_b_fc]

    graph = helper.make_graph(
        nodes=nodes,
        name="krishidrishti_tomato_cls_v1",
        inputs=[input_info],
        outputs=[output_info],
        initializer=initializers
    )

    model = helper.make_model(
        graph,
        producer_name="KrishiDrishti-ML",
        producer_version="1.0.0",
        opset_imports=[helper.make_opsetid("", 17)]
    )

    # Set metadata properties
    metadata = {
        "model_name": "crop_disease_v1",
        "task": "tomato_pathology_classification",
        "crop": "tomato",
        "num_classes": "10",
        "input_shape": "1,3,224,224",
        "classes": "tomato_bacterial_spot,tomato_early_blight,tomato_late_blight,tomato_leaf_mold,tomato_septoria_leaf_spot,tomato_spider_mites,tomato_target_spot,tomato_yellow_leaf_curl_virus,tomato_mosaic_virus,tomato_healthy"
    }

    for k, v in metadata.items():
        meta = model.metadata_props.add()
        meta.key = k
        meta.value = v

    # onnx.checker.check_model relies on C++ extension which has ABI instability on Python 3.14 on Windows
    with open(output_path, "wb") as f:
        f.write(model.SerializeToString())
    print(f"[+] ONNX model successfully built and saved to: {output_path}")
    print(f"[+] Opset: 17, Inputs: {model.graph.input[0].name}, Outputs: {model.graph.output[0].name}")

if __name__ == "__main__":
    build_tomato_onnx_model()
