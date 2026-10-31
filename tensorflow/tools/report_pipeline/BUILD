package(default_visibility = ["//visibility:public"])

py_binary(
    name = "history_replay",
    srcs = ["history_replay.py"],
    main = "history_replay.py",
    deps = ["//tensorflow/python/eager/plan_runtime:plan_runtime"],
)

py_binary(
    name = "tf_graph_report",
    srcs = ["tf_graph_report.py"],
    main = "tf_graph_report.py",
    deps = [
        "//tensorflow/python/eager/plan_runtime:plan_runtime",
        "//tensorflow/python:framework",
    ],
)
