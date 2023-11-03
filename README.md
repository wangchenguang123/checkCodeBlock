# checkCodeBlock
use tree-sitter to get same structure  codeBlock for target code

我们想分析已知的目标代码片段 位于源文件代码片段中的位置，同时通过tree-sitter获取与已知代码片段结构相同的代码片段并存储，以便做深入分析。
目前计划从函数级别，代码块级别入手，后续会计划从文件级别入手，深入分析。
