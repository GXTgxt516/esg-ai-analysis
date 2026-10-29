import streamlit as st
import requests
import fitz  # PyMuPDF，用于读取PDF文件

st.set_page_config(page_title="ESG报告智能解析平台", layout="wide")
st.title("📄 ESG报告智能解析平台")

# 读取智谱密钥
API_KEY = st.secrets.get("ZHIPU_API_KEY")
if not API_KEY:
    st.error("❌ 未读取到智谱API KEY！请到Streamlit后台配置密钥")
    st.stop()

# 智谱调用函数，固定使用免费 glm-4-flash
def call_ai(prompt):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    res = requests.post(url, headers=headers, json=body, timeout=60)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

# PDF文本提取函数
def extract_pdf_text(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

# 页面功能
upload_file = st.file_uploader("上传ESG报告PDF文件", type="pdf")
if upload_file is not None:
    with st.spinner("正在提取PDF文本..."):
        pdf_content = extract_pdf_text(upload_file)
    st.success("✅ 文件读取完成！")

    tab1, tab2, tab3 = st.tabs(["报告摘要", "关键问题提取", "自定义问答"])
    with tab1:
        if st.button("生成ESG摘要"):
            with st.spinner("AI正在总结报告..."):
                prompt = f"你是ESG分析专家，基于下面这份ESG报告内容，精简总结环境、社会、治理三方面核心信息：\n{pdf_content[:12000]}"
                result = call_ai(prompt)
                st.write(result)
    with tab2:
        if st.button("提取高频重点问题"):
            with st.spinner("AI提取重点..."):
                prompt = f"阅读这份ESG报告，列出里面的风险点、待改进事项：\n{pdf_content[:12000]}"
                result = call_ai(prompt)
                st.write(result)
    with tab3:
        user_question = st.text_input("向这份报告提问：")
        if user_question:
            with st.spinner("AI回答中..."):
                prompt = f"基于这份ESG报告内容回答用户问题，只依据文档内容回答：\n文档：{pdf_content[:12000]}\n用户问题：{user_question}"
                result = call_ai(prompt)
                st.write(result)
