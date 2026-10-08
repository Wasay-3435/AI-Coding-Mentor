from backend.app.chains.code_analysis_chain import code_analysis_chain


result = code_analysis_chain.invoke({
    "language": "python",
    "code": "print(x)",
})


print(result)
print(type(result))