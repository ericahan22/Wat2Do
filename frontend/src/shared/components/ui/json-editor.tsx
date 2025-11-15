import { useEffect, useRef, useState } from "react";
import { EditorView, basicSetup } from "codemirror";
import { EditorState } from "@codemirror/state";
import { json } from "@codemirror/lang-json";
import { oneDark } from "@codemirror/theme-one-dark";
import { hoverTooltip } from "@codemirror/view";

export default function JSONEditor() {
  const editorRef = useRef(null);
  const viewRef = useRef(null);
  const [value, setValue] = useState(`{
  "username": [
    "natgeo",
    "https://www.instagram.com/natgeo/",
    "https://www.instagram.com/p/DLNsnpUTdVS/"
  ]
}`);

  // Custom hover tooltip
  const customTooltip = hoverTooltip((view, pos) => {
    const { from, to } = view.state.doc.lineAt(pos);
    const line = view.state.doc.sliceString(from, to);

    // Check if hovering over "username" field
    if (line.includes('"username"')) {
      return {
        pos,
        above: true,
        create() {
          const dom = document.createElement("div");
          dom.className = "cm-tooltip-custom";
          dom.innerHTML = `
            <div style="padding: 8px 12px; max-width: 300px;">
              <div style="font-weight: 600; margin-bottom: 4px; color: #c792ea;">
                🔗 Instagram username, profile URL, or post URL
              </div>
              <div style="font-size: 13px; color: #b0b0b0;">
                Insert the username or URL of any profile you want to get posts from. 
                You can also paste the post URLs.
              </div>
            </div>
          `;
          return { dom };
        },
      };
    }
    return null;
  });

  useEffect(() => {
    if (!editorRef.current) return;

    const startState = EditorState.create({
      doc: value,
      extensions: [
        basicSetup,
        json(),
        oneDark,
        customTooltip,
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            setValue(update.state.doc.toString());
          }
        }),
        EditorView.theme({
          "&": {
            fontSize: "14px",
            height: "400px",
          },
          ".cm-content": {
            fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
          },
          ".cm-tooltip-custom": {
            backgroundColor: "#2d3748",
            border: "1px solid #4a5568",
            borderRadius: "6px",
            color: "#e2e8f0",
          },
        }),
      ],
    });

    const view = new EditorView({
      state: startState,
      parent: editorRef.current,
    });

    viewRef.current = view as unknown as null;

    return () => {
      view.destroy();
    };
  }, []);

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-4">
        <div className="flex gap-2 mb-3">
          <button className="px-4 py-2 bg-gray-700 text-white rounded-lg font-medium">
            Manual
          </button>
          <button className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg font-medium hover:bg-gray-700">
            JSON
          </button>
        </div>

        <div className="border border-gray-700 rounded-lg overflow-hidden">
          <div ref={editorRef} />
        </div>

        <p className="mt-3 text-sm text-gray-400">
          💡 Hover over{" "}
          <code className="bg-gray-800 px-2 py-1 rounded">"username"</code> to
          see the tooltip
        </p>
      </div>

      <div className="mt-6 p-4 bg-gray-800 rounded-lg">
        <h3 className="font-semibold mb-2 text-white">Current Value:</h3>
        <pre className="text-xs text-gray-300 overflow-auto">{value}</pre>
      </div>
    </div>
  );
}
