import streamlit as st
from openai import OpenAI

# -----------------------------
# SIMPLE STOCK ANALYSIS CHAT
# GPT-powered, no scraping, trader-focused
# -----------------------------

def initialize_chat():
    """Initialize chat session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def analyze_stock(question, api_key, model="gpt-3.5-turbo"):
    """
    Analyze stock with AI - trader-focused insights
    
    Args:
        question: User's question
        api_key: OpenAI API key
        model: Model to use 
    
    Returns:
        AI response
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Expert trader prompt
        system_prompt = """You are an expert Indian stock market trader and fundamental analyst.

                        RESPONSE FORMAT - Use this EXACT 4-column table structure for better Streamlit display:

                        **[COMPANY NAME] - Current Price: ₹[PRICE]**

                        | 📊 VALUATION | ⭐ PROFITABILITY | 📈 GROWTH | 💼 BALANCE SHEET |
                        |--------------|------------------|-----------|------------------|
                        | **Market Cap** = ₹[X]T/B | **Revenue (TTM)** = ₹[X]T/B | **Revenue 3Y CAGR** = [X]% | **Debt/Equity** = [X] |
                        | **EPS (TTM)** = ₹[X] | **Net Profit (TTM)** = ₹[X]T/B | **Profit YoY** = [X]% | **Current Ratio** = [X] |
                        | **P/E Ratio** = [X] | **Operating Margin** = [X]% | **EPS Growth** = [X]% | **Interest Coverage** = [X]x |
                        | **Sector P/E** = [X] | **Net Margin** = [X]% | **Sales Growth** = [X]% | **Debt** = ₹[X]T/B |
                        | **P/B Ratio** = [X] | **ROE** = [X]% | **PAT Growth** = [X]% | **Working Capital** = ₹[X]T/B |
                        | **PEG Ratio** = [X] | **ROCE** = [X]% | | |

                        **📝 ANALYSIS**

                        | Aspect | Assessment |
                        |--------|------------|
                        | **Valuation** | [Overvalued/Fairly Valued/Undervalued] - [brief reason] |
                        | **Quality Score** | [Excellent/Good/Average/Poor] - [brief reason] |
                        | **Growth Momentum** | [Strong/Moderate/Weak] - [brief reason] |
                        | **Financial Health** | [Strong/Moderate/Weak] - [brief reason] |

                        **🎯 TRADING RECOMMENDATION**

                        | Parameter | Details |
                        |-----------|---------|
                        | **Call** | **[BUY/SELL/HOLD]** |
                        | **Entry Zone** | ₹[X] - ₹[Y] |
                        | **Target (12M)** | ₹[X] |
                        | **Stop Loss** | ₹[X] |
                        | **Risk-Reward** | 1:[X] |

                        **⚠️ KEY RISKS**
                        1. [Risk 1]
                        2. [Risk 2]

                        EXAMPLE:

                        **Reliance Industries - Current Price: ₹2,400**

                        | 📊 VALUATION | ⭐ PROFITABILITY | 📈 GROWTH | 💼 BALANCE SHEET |
                        |--------------|------------------|-----------|------------------|
                        | **Market Cap** = ₹15T | **Revenue (TTM)** = ₹6T | **Revenue 3Y CAGR** = 9% | **Debt/Equity** = 0.5 |
                        | **EPS (TTM)** = ₹114 | **Net Profit (TTM)** = ₹1T | **Profit YoY** = 12% | **Current Ratio** = 1.2 |
                        | **P/E Ratio** = 21.05 | **Operating Margin** = 14% | **EPS Growth** = 10% | **Interest Coverage** = 8.5x |
                        | **Sector P/E** = 15.00 | **Net Margin** = 16.67% | **Sales Growth** = 11% | **Debt** = ₹2.5T |
                        | **P/B Ratio** = 2.5 | **ROE** = 12% | **PAT Growth** = 12% | **Working Capital** = ₹1.2T |
                        | **PEG Ratio** = 1.75 | **ROCE** = 10% | | |

                        **📝 ANALYSIS**

                        | Aspect | Assessment |
                        |--------|------------|
                        | **Valuation** | Fairly Valued - P/E premium justified by diversified business model |
                        | **Quality Score** | Good - Strong margins, improving ROE, manageable debt levels |
                        | **Growth Momentum** | Moderate - Steady growth across retail, telecom, and energy |
                        | **Financial Health** | Strong - Low debt/equity, healthy cash flows, strong coverage ratios |

                        **🎯 TRADING RECOMMENDATION**

                        | Parameter | Details |
                        |-----------|---------|
                        | **Call** | **HOLD** |
                        | **Entry Zone** | ₹2,200 - ₹2,300 |
                        | **Target (12M)** | ₹2,700 |
                        | **Stop Loss** | ₹2,100 |
                        | **Risk-Reward** | 1:2.5 |

                        **⚠️ KEY RISKS**
                        1. Crude oil price volatility affects refining margins (40% of EBITDA)
                        2. High capex commitments in telecom and retail may pressure cash flows

                        RULES:
                        - ALWAYS use this exact 4-column table format
                        - Fill ALL cells with specific numbers
                        - Use T for trillion, B for billion, Cr for crores
                        - Include ALL metrics shown in the template
                        - For Indian stocks: use ₹
                        - For US stocks: use $
                        - Keep analysis brief (1 line each)
                        - Always include entry/target/stop loss prices"""

        # Keep only last 3 messages for context (save tokens)
        messages = [{"role": "system", "content": system_prompt}]
        
        if "messages" in st.session_state and len(st.session_state.messages) > 0:
            for msg in st.session_state.messages[-3:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"][:700]
                })
        
        messages.append({"role": "user", "content": question})
        
        # API call - optimized for cost
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4,      # Balanced for analysis
            max_tokens=700,       # Enough for detailed analysis
            top_p=0.95,
            frequency_penalty=0.3
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

def render_stock_chat(api_key, model="gpt-3.5-turbo"):
    """
    Render stock analysis chat interface
    
    Args:
        api_key: OpenAI API key
        model: Model to use
    """
    
    initialize_chat()
    
    # Sidebar - Chat Stats
    with st.sidebar:
        st.divider()
        
        st.markdown("#### 📊 Chat Statistics")
        
        msg_count = len(st.session_state.messages)
        
        if msg_count > 0:
            # Accurate token estimation
            # Input tokens: question + context + system prompt (~60% of total)
            # Output tokens: AI response (~40% of total)
            total_tokens = msg_count * 200
            input_tokens = int(total_tokens * 0.60)   # 60% input
            output_tokens = int(total_tokens * 0.40)  # 40% output
            
            # Real OpenAI pricing (per 1M tokens)
            if model == "gpt-3.5-turbo":
                input_rate = 0.50    # $0.50 per 1M input tokens
                output_rate = 1.50   # $1.50 per 1M output tokens
                cost_per_q_usd = 0.0008
            elif model == "gpt-4o-mini":
                input_rate = 0.15    # $0.15 per 1M input tokens  
                output_rate = 0.60   # $0.60 per 1M output tokens
                cost_per_q_usd = 0.0003
            elif model == "gpt-4":
                input_rate = 30.00   # $30 per 1M input tokens
                output_rate = 60.00  # $60 per 1M output tokens
                cost_per_q_usd = 0.036
            elif model == "gpt-4-turbo":
                input_rate = 10.00   # $10 per 1M input tokens
                output_rate = 30.00  # $30 per 1M output tokens
                cost_per_q_usd = 0.016
            else:
                input_rate = 0.50
                output_rate = 1.50
                cost_per_q_usd = 0.0008
            
            # Calculate actual cost
            input_cost_usd = (input_tokens / 1_000_000) * input_rate
            output_cost_usd = (output_tokens / 1_000_000) * output_rate
            total_cost_usd = input_cost_usd + output_cost_usd
            
            # Convert to INR (1 USD = ₹83)
            exchange_rate = 83
            total_cost_inr = total_cost_usd * exchange_rate
            cost_per_q_inr = cost_per_q_usd * exchange_rate
            
            # Inline display
            st.markdown(f"""
            <div style='font-size: 12px; line-height: 1.8; margin-top: -10px;'>
                <div style='color: #888; margin-bottom: 4px;'>
                    💵 <b>Cost per question:</b> ${cost_per_q_usd:.5f} (₹{cost_per_q_inr:.3f})
                </div>
                <div>
                    <b>Msgs:</b> {msg_count} | <b>In:</b> {input_tokens:,} <b>Out:</b> {output_tokens:,} | <b>Cost:</b> ${total_cost_usd:.5f} (₹{total_cost_inr:.3f})
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Cost breakdown
            with st.expander("💵 Pricing Details"):
                st.caption(f"**Model:** {model}")
                st.caption(f"**Input tokens:** {input_tokens:,} × ${input_rate:.2f}/1M = ${input_cost_usd:.5f}")
                st.caption(f"**Output tokens:** {output_tokens:,} × ${output_rate:.2f}/1M = ${output_cost_usd:.5f}")
                st.caption(f"**Total:** ${total_cost_usd:.5f} (₹{total_cost_inr:.3f})")
                st.caption(f"**Exchange:** 1 USD = ₹{exchange_rate}")
                
                if msg_count >= 50:
                    st.warning("💡 Clear chat to reduce tokens")
        else:
            st.caption("No messages yet")
        
        st.divider()
        
        # Clear button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    st.subheader("💬 Stock Analysis Assistant")
    
    # Quick examples
    with st.expander("💡 Example Questions"):
        st.markdown("""
        **Indian Stocks:**
        - "Analyze RELIANCE fundamentals"
        - "Should I buy TCS at current price?"
        - "INFY vs TCS which is better?"
        - "Is HDFC Bank overvalued?"
        - "TATA MOTORS trading analysis"
        
        **US Stocks:**
        - "AAPL fundamental analysis"
        - "Is NVDA a buy?"
        - "Compare MSFT vs GOOGL"
        
        **Tips:**
        - Mention stock name or symbol
        - Ask for specific analysis (valuation, buy/sell, comparison)
        - Be specific about your trading horizon
        """)
    
    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about any stock... (e.g., 'Analyze RELIANCE')"):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = analyze_stock(prompt, api_key, model)
                st.markdown(response)
        
        # Save response
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()