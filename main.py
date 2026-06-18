# Standard and third party package imports
import asyncio
import os
import sys
from nicegui import ui, app, run


# Appends your local project layout cleanly to Python's system paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Internal logic imports
from scripts.query_processing_01 import processor_service
from scripts.retrieval_layer_02 import retriever_service
from scripts.reranking_layer_03 import rerank_service
from scripts.build_context_04 import build_context
from scripts.llm_generation_05 import local_model

# App-wide global styles
ui.add_head_html('''
<style>
    body {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: ui-sans-serif, system-ui, sans-serif;
    }
    #c3.nicegui-content{
        padding: 0px
    }
    /* Custom scrollbar for chat history */
    .custom-scroll::-webkit-scrollbar {
        width: 6px;
    }
    .custom-scroll::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
        background: #374151;
        border-radius: 3px;
    }
    .search-input{
        width: 100%;
        max-width: 56rem; 
        background-color: #E2E8F0; 
        border: 1px solid #1e293b; 
        border-radius: 1rem; 
        padding: 0.5rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); 
        position: relative;
        align-items: center;
    }

    .search-input .q-btn-item{
        background-color: #020617;
        opacity: 0.7;
    }
    .search-input .q-btn-item:hover{
        opacity: 1;
    }
</style>
''')

history = []


# --- Business Logic ---
async def rag_search_stream(user_query: str, container):
    """Handles the RAG pipeline steps asynchronously to show UI updates."""
    history.append(user_query)

    with container:
        # User message card
        with ui.card().classes('w-full bg-slate-800 border border-slate-700/50 p-4 rounded-xl shadow-md mb-4'):
            with ui.row().classes('items-center gap-2 text-slate-400 text-xs font-semibold uppercase mb-1'):
                ui.icon('person', size='xs')
                ui.label('You')
            ui.label(user_query).classes('text-base text-slate-100')

        # AI Assistant dynamic response card
        with ui.card().classes('w-full bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-lg mb-4'):
            with ui.row().classes('items-center gap-2 text-emerald-400 text-xs font-semibold uppercase mb-3'):
                ui.icon('smart_toy', size='xs')
                ui.label('Assistant')

            # Status step container
            status_container = ui.row().classes(
                'items-center gap-3 bg-slate-850 p-3 rounded-lg border border-slate-800 w-full text-slate-300 text-sm')
            with status_container:
                spinner = ui.spinner(type='dots', size='sm', color='emerald')
                status_text = ui.label("Initializing...")

            # Helper function to update status UI instantly
            async def update_step(text: str, finished: bool = False):
                status_text.text = text
                if finished:
                    spinner.delete()
                    status_container.classes('bg-emerald-950/30 border-emerald-900/50 text-emerald-300',
                                             remove='bg-slate-850 border-slate-800 text-slate-300')
                await asyncio.sleep(0.05)

            # 1. Processing
            await update_step("Analyzing and processing query...")
            processed_query = processor_service.process_query(user_query)

            # 2. Retrieval
            await update_step("Searching knowledge base for relevant documents...")
            retrieved_docs = retriever_service.search_knowledge_base(processed_query)

            # 3. Reranking
            await update_step("Evaluating and reranking document relevance...")
            ranked_documents = rerank_service.rerank(user_query, retrieved_docs)

            # 4. Context
            await update_step("Building optimized context payload...")
            context, token_count = build_context(ranked_documents, 3100)

            # 5. LLM Generation
            await update_step("Synthesizing final response...")
            result = await run.io_bound(local_model.prompt_model, user_query, context)

            # Complete
            await update_step("Pipeline completed successfully", finished=True)

            # Append Markdown answer cleanly (ONLY ONCE)
            ui.element('div').classes('h-px bg-slate-800 w-full my-4')
            ui.markdown(result.content).classes(
                'text-slate-200 leading-relaxed markdown-body w-full'
            )

    # Give NiceGUI a quick moment to render the layout cards into the DOM
    await asyncio.sleep(0.1)

    # Target the response element to bring it into view smoothly
    await ui.run_javascript(f'''
    const container = getElement({container.id}) || document.getElementById("{container.id}");
    const target = container ? container.lastElementChild : null;

    if (target) {{
        target.scrollIntoView({{
            behavior: 'smooth',
            block: 'start'
        }});
    }}
    ''')

async def handle_send(e):
    if e.args and e.args.get('shiftKey'):
        question.value += '\n'
        return

    query = question.value.strip()
    if not query:
        return

    question.value = ""


    with history_container:
        with ui.row().classes(
                'w-full items-center gap-2 p-2 hover:bg-slate-800 rounded-lg cursor-pointer transition-colors group'):
            ui.icon('chat_bubble_outline', size='xs').classes('text-slate-500 group-hover:text-slate-300')
            ui.label(query if len(query) < 25 else f"{query[:22]}...").classes(
                'text-sm text-slate-400 group-hover:text-slate-200 truncate')

    if len(history) == 0:
        chat_container.clear()

    chat_container.update()

    await ui.run_javascript(f'''
    setTimeout(() => {{
        const el = getElement({chat_container.id});
        if (el) {{
            el.scrollTo({{
                top: el.scrollHeight,
                behavior: 'smooth'
            }});
        }}
    }}, 50);
    ''')
    await rag_search_stream(query, chat_container)

# --- UI Layout Design ---
with ui.row().classes('w-full h-screen no-wrap gap-0 bg-[#0b0f19]'):
    # ================= LEFT SIDEBAR =================
    with ui.column().classes(
            'w-64 h-full bg-slate-950 border-r border-slate-900 p-4 flex-shrink-0 flex justify-between'):
        with ui.column().classes('w-full gap-4'):
            with ui.row().classes('items-center gap-2 px-2 py-1'):
                ui.icon('auto_awesome', size='sm').classes('text-emerald-400')
                ui.label("RAG Studio").classes('text-lg font-bold tracking-wide text-slate-100')

            ui.element('div').classes('h-px bg-slate-900 w-full')
            ui.label("Recent Activity").classes('text-xs font-semibold uppercase tracking-wider text-slate-500 px-2')

            history_container = ui.column().classes('w-full gap-1 overflow-y-auto custom-scroll max-h-[70vh]')

        ui.label("v1.2.0 • Built by Jeslor").classes('text-center text-xs text-slate-600 w-full')

    # ================= MAIN AREA =================
    with ui.column().classes('flex-1 h-full relative items-center justify-between gap-0'):
        with ui.row().classes(
                'w-full justify-between items-center px-8 py-4 border-b border-slate-900/60 bg-slate-950/20 backdrop-blur'):
            ui.label("Pipeline Workspace").classes('font-medium text-slate-300')
            ui.badge('Connected', color='positive').classes('px-2 py-0.5 text-xs')

        chat_container = ui.column().classes(
            'w-full max-w-4xl flex-1 overflow-y-auto p-6 md:p-8 custom-scroll mb-32 pb-10')
        with chat_container:
            with ui.column().classes('w-full items-center justify-center py-20 text-center gap-3 text-slate-500'):
                ui.icon('explore', size='xl').classes('text-slate-700')
                ui.label("Ready for instructions").classes('text-lg font-medium text-slate-400')
                ui.label("Submit a query below to monitor the retrieval processing stream.").classes('text-sm max-w-sm')

        with ui.row().classes(
                'absolute bottom-0 left-0 right-0 justify-center p-6 bg-gradient-to-t from-[#0b0f19] via-[#0b0f19]/95 to-transparent'):
            with ui.row().classes('search-input'):
                question = ui.textarea(
                    placeholder='Ask your knowledge base anything...'
                ).props('autogrow borderless lines=1').classes(
                    'flex-1 text-slate-200 px-4 py-2 bg-transparent text-base focus:outline-none')

                question.on('keydown.enter.prevent', handle_send, args=['shiftKey'])

                with ui.button(icon='arrow_upward', on_click=lambda e: handle_send(e)).props(
                        'round color=emerald elevation=0').classes(
                    'transition-transform active:scale-95 flex-shrink-0 m-1'):
                    ui.tooltip('Execute RAG query (Enter)')


# --- Desktop Window Taskbar/Dock Configuration ---
def setup_desktop_environment():
    icon_path = os.path.join("assets", "favicon.ico")

    if sys.platform == "win32":
        try:
            import ctypes
            myappid = 'jeslor.localragstudio.workspace.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    elif sys.platform == "darwin":
        try:
            from AppKit import NSApplication, NSImage, NSApplicationActivationPolicyAccessory
            app_instance = NSApplication.sharedApplication()
            app_instance.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

            if os.path.exists(icon_path):
                icon_image = NSImage.alloc().initWithContentsOfFile_(icon_path)
                if icon_image:
                    app_instance.setApplicationIconImage_(icon_image)
        except Exception:
            pass


# Connect initialization wrapper to NiceGUI global hooks
def on_startup():
    setup_desktop_environment()


app.on_startup(on_startup)

# Run Native Desktop Window Core Loops
ui.run(
    title="RAG Assistant Workspace",
    favicon=os.path.join("assets", "favicon.ico"),
    native=True,
    reload=False,
)