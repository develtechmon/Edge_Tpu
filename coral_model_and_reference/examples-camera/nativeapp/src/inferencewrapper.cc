#include "inferencewrapper.h"

#include <fstream>
#include <iostream>
#include <memory>
#include <string>

#include "tensorflow/lite/builtin_op_data.h"
#include "tensorflow/lite/kernels/register.h"
#include "tensorflow/lite/model.h"
#include "tflite/public/edgetpu.h"

#define TFLITE_MINIMAL_CHECK(x)                              \
  if (!(x)) {                                                \
    fprintf(stderr, "Error at %s:%d\n", __FILE__, __LINE__); \
    exit(EXIT_FAILURE);                                      \
  }

namespace coral {

namespace {
std::vector<std::string> read_labels(const std::string& label_path) {
  std::vector<std::string> labels;

  std::ifstream label_file(label_path);
  std::string line;
  if (label_file.is_open()) {
    while (getline(label_file, line)) {
      labels.push_back(line);
    }
  } else {
    std::cerr << "Unable to open file " << label_path << std::endl;
    exit(EXIT_FAILURE);
  }

  return labels;
}

}  // namespace

InferenceWrapper::InferenceWrapper(const std::string& model_path, const std::string& label_path) {
  auto model = tflite::FlatBufferModel::BuildFromFile(model_path.c_str());
  TFLITE_MINIMAL_CHECK(model != nullptr);

  edgetpu_context_ = edgetpu::EdgeTpuManager::GetSingleton()->OpenDevice();
  tflite::ops::builtin::BuiltinOpResolver resolver;
  resolver.AddCustom(edgetpu::kCustomOp, edgetpu::RegisterCustomOp());

  if (tflite::InterpreterBuilder(*model, resolver)(&interpreter_) != kTfLiteOk) {
    std::cout << "Failed to build Interpreter\n";
    exit(EXIT_FAILURE);
  }
  interpreter_->SetExternalContext(kTfLiteEdgeTpuContext, edgetpu_context_.get());
  interpreter_->SetNumThreads(1);
  TFLITE_MINIMAL_CHECK(interpreter_->AllocateTensors() == kTfLiteOk);

  labels_ = read_labels(label_path);
}

std::pair<std::string, float> InferenceWrapper::RunInference(
    const uint8_t* input_data, int input_size) {
  std::vector<float> output_data;
  uint8_t* input = interpreter_->typed_input_tensor<uint8_t>(0);
  std::memcpy(input, input_data, input_size);

  TFLITE_MINIMAL_CHECK(interpreter_->Invoke() == kTfLiteOk);

  const auto& output_indices = interpreter_->outputs();
  const auto* out_tensor = interpreter_->tensor(output_indices[0]);
  TFLITE_MINIMAL_CHECK(out_tensor != nullptr);

  float max_prob;
  int max_index;
  if (out_tensor->type == kTfLiteUInt8) {
    const uint8_t* output = interpreter_->typed_output_tensor<uint8_t>(0);
    max_index = std::max_element(output, output + out_tensor->bytes) - output;
    max_prob = (output[max_index] - out_tensor->params.zero_point) * out_tensor->params.scale;
  } else if (out_tensor->type == kTfLiteFloat32) {
    const float* output = interpreter_->typed_output_tensor<float>(0);
    max_index = std::max_element(output, output + out_tensor->bytes / sizeof(float)) - output;
    max_prob = output[max_index];
  } else {
    std::cerr << "Tensor " << out_tensor->name
              << " has unsupported output type: " << out_tensor->type << std::endl;
    exit(EXIT_FAILURE);
  }

  return {labels_[max_index], max_prob};
}

}  // namespace coral
