# Testing RAG v1 System

## 🧪 Quick Test Guide

The RAG system is now live! Here's how to test it:

### **1. Verify RAG is Available**

In the Streamlit app sidebar, you should see:
```
Use RAG (vector store) - ✅ Available
```

If you see "❌ Not available", run:
```bash
python ingest.py
```

### **2. Enable RAG**

1. **Toggle ON** "Use RAG (vector store)" in sidebar
2. The toggle should show "✅ Available"

### **3. Test Queries**

Try these queries to see RAG in action:

#### **Diabetes Questions**
```
"What are the early warning signs of diabetes?"
"What questions should I ask my doctor about diabetes?"
"How can I manage diabetes with lifestyle changes?"
```

#### **Hypertension Questions**
```
"What is considered high blood pressure?"
"How can I lower my blood pressure naturally?"
"What medications are used for high blood pressure?"
```

#### **Navigation Questions**
```
"How do I prepare for my next doctor visit?"
"What does my blood test mean?"
"How do I find the right specialist?"
```

#### **Insurance/Medication Questions**
```
"What does this insurance EOB mean?"
"How do I manage multiple medications safely?"
"What should I know about medication interactions?"
```

### **4. What to Look For**

#### **Enhanced Responses**
- More detailed, specific information
- References to specific conditions or procedures
- Actionable advice and next steps

#### **Citations Section**
After each response with RAG enabled, you should see:
```
---
### 📚 Sources
**Diabetes** - Early Warning Signs
**Diabetes** - Risk Factors
**Doctor Visit Prep** - Communication Tips
```

#### **Context Integration**
The LLM should reference specific information from the knowledge base with inline citations like `[Diabetes]` or `[Hypertension]`.

### **5. Compare With/Without RAG**

**Test the difference:**
1. Ask a question with RAG **OFF**
2. Note the response
3. Toggle RAG **ON** 
4. Ask the same question
5. Compare the responses

You should see:
- **Without RAG**: General, broad responses
- **With RAG**: Specific, detailed responses with citations

### **6. Test Edge Cases**

#### **Safety Integration**
```
"I'm having chest pain" 
→ Should still show emergency message (no RAG used)
```

#### **Out-of-Scope Queries**
```
"What's the weather like?"
→ Should work normally (no relevant RAG results)
```

#### **Complex Queries**
```
"I have diabetes and high blood pressure. What should I ask my doctor?"
→ Should retrieve relevant info from both knowledge areas
```

### **7. Check Metrics**

In the sidebar, verify:
- **RAG toggle** shows enabled status
- **Message metadata** includes `rag_used: true`
- **Citations** appear below responses

### **8. Troubleshooting**

#### **RAG Not Working**
- Check if toggle shows "❌ Not available"
- Run `python ingest.py` to rebuild index
- Restart Streamlit app

#### **No Citations**
- Ensure RAG toggle is ON
- Check that query is health-related
- Verify knowledge base has relevant content

#### **Poor Results**
- Try rephrasing your question
- Use more specific health terminology
- Check if topic is covered in corpus

## 🎯 Expected Results

### **Sample Query: "What are the early signs of diabetes?"**

**With RAG Enabled:**
```
Based on our knowledge base, the early warning signs of diabetes include:

• Increased thirst and frequent urination [Diabetes]
• Fatigue and weakness [Diabetes]  
• Blurred vision [Diabetes]
• Slow-healing cuts or sores [Diabetes]
• Tingling or numbness in hands or feet [Diabetes]
• Unexplained weight loss [Diabetes]

These symptoms occur because your body is struggling to process blood sugar properly. If you're experiencing these signs, it's important to discuss them with your healthcare provider, who can order appropriate tests like a fasting blood glucose test or A1C test [Diabetes].

---

### 📚 Sources
**Diabetes** - Early Warning Signs
**Diabetes** - Diagnosis
**Diabetes** - Risk Factors
```

**Without RAG:**
```
The early signs of diabetes can vary, but common symptoms include increased thirst, frequent urination, fatigue, and blurred vision. If you're concerned about diabetes, please consult with your healthcare provider for proper evaluation and testing.
```

## ✅ Success Indicators

- ✅ RAG toggle shows "Available" status
- ✅ Responses include specific information from knowledge base
- ✅ Citations appear below responses
- ✅ Inline source references in text
- ✅ More detailed and actionable responses
- ✅ Safety checks still work (emergency queries blocked)

## 🚀 Ready for Production

The RAG system is fully functional and ready for user testing. It provides:

- **Enhanced accuracy** through knowledge base context
- **Source transparency** with citations
- **Professional credibility** with referenced information
- **Seamless integration** with existing safety and LLM systems

Test it out and see how it transforms the quality of health-related responses! 🎉
