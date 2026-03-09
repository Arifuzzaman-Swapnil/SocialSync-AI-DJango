import { useState, useEffect, useRef } from 'react';
import { InformationCircleIcon, ClipboardDocumentIcon, CheckIcon, ArrowPathIcon, ClockIcon } from '@heroicons/react/24/outline';
import { Modal } from './Modal';
import type { PromptHistoryEntry } from '../../types';

interface PromptInfoButtonProps {
  prompt: string;
  label?: string;
  size?: 'sm' | 'md';
  onRegenerate?: (editedPrompt: string) => void | Promise<void>;
  regenerating?: boolean;
  regenerateLabel?: string;
  promptHistory?: PromptHistoryEntry[];
  onLoadHistory?: () => void;
  historyLoading?: boolean;
}

export function PromptInfoButton({
  prompt,
  label = 'AI Prompt Used',
  size = 'sm',
  onRegenerate,
  regenerating = false,
  regenerateLabel = 'Regenerate with this prompt',
  promptHistory,
  onLoadHistory,
  historyLoading = false,
}: PromptInfoButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [editedPrompt, setEditedPrompt] = useState(prompt);
  const [hoveredEntry, setHoveredEntry] = useState<number | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ top: number; left: number } | null>(null);
  const historyRef = useRef<HTMLDivElement>(null);

  // Sync editedPrompt when the source prompt changes (e.g. after regeneration)
  useEffect(() => {
    setEditedPrompt(prompt);
  }, [prompt]);

  // Auto-load history when modal opens
  useEffect(() => {
    if (isOpen && onLoadHistory) {
      onLoadHistory();
    }
  }, [isOpen]);

  if (!prompt) return null;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(editedPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRegenerate = async () => {
    if (!onRegenerate || regenerating) return;
    await onRegenerate(editedPrompt);
  };

  const handleUseHistoryPrompt = (historyPrompt: string) => {
    setEditedPrompt(historyPrompt);
  };

  const handleEntryHover = (entryId: number, e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltipPos({
      top: rect.top,
      left: rect.right + 12,
    });
    setHoveredEntry(entryId);
  };

  const isEditable = !!onRegenerate;
  const hasEdits = editedPrompt !== prompt;
  const hasHistory = onLoadHistory != null;

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    return d.toLocaleDateString();
  };

  const hoveredPromptText = hoveredEntry != null
    ? promptHistory?.find(e => e.id === hoveredEntry)?.prompt_text
    : null;

  return (
    <>
      <button
        onClick={(e) => { e.stopPropagation(); setIsOpen(true); }}
        className="inline-flex items-center justify-center text-text-tertiary hover:text-accent transition-colors"
        title="View AI prompt used"
      >
        <InformationCircleIcon className={size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'} />
      </button>

      <Modal isOpen={isOpen} onClose={() => { setIsOpen(false); setEditedPrompt(prompt); setHoveredEntry(null); }} title={label} size="xxl">
        <div className="space-y-4">
          {/* Prompt display / editor */}
          <div className="relative">
            {isEditable ? (
              <textarea
                className="w-full text-sm text-text-secondary bg-dark-800 border border-white/5 rounded-xl p-5 max-h-[50vh] min-h-[280px] overflow-y-auto font-mono leading-relaxed resize-y focus:outline-none focus:ring-1 focus:ring-primary-500/50 focus:border-primary-500/30"
                value={editedPrompt}
                onChange={(e) => setEditedPrompt(e.target.value)}
                spellCheck={false}
              />
            ) : (
              <pre className="whitespace-pre-wrap text-sm text-text-secondary bg-dark-800 border border-white/5 rounded-xl p-5 max-h-[55vh] overflow-y-auto font-mono leading-relaxed">
                {prompt}
              </pre>
            )}
          </div>

          {/* Info text */}
          <p className="text-xs text-text-tertiary">
            {isEditable
              ? 'This is the prompt sent to the AI. You can edit it and regenerate for a different output.'
              : 'This is the exact prompt that was sent to the AI model to generate this content.'}
          </p>

          {/* Action buttons */}
          <div className="flex items-center justify-between pt-1">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-dark-700 hover:bg-dark-600 text-text-tertiary hover:text-text-primary transition-colors"
              title="Copy prompt"
            >
              {copied ? (
                <><CheckIcon className="w-3.5 h-3.5 text-success" /> Copied!</>
              ) : (
                <><ClipboardDocumentIcon className="w-3.5 h-3.5" /> Copy</>
              )}
            </button>

            {isEditable && (
              <div className="flex items-center gap-2">
                {hasEdits && (
                  <button
                    onClick={() => setEditedPrompt(prompt)}
                    className="text-xs text-text-muted hover:text-text-secondary transition-colors"
                  >
                    Reset
                  </button>
                )}
                <button
                  onClick={handleRegenerate}
                  disabled={regenerating || !editedPrompt.trim()}
                  className="flex items-center gap-1.5 text-xs px-4 py-1.5 rounded-lg bg-primary-500 hover:bg-primary-400 text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {regenerating ? (
                    <><div className="animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full" /> Regenerating...</>
                  ) : (
                    <><ArrowPathIcon className="w-3.5 h-3.5" /> {regenerateLabel}</>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Prompt History — always visible when available */}
          {hasHistory && (
            <div className="border-t border-white/5 pt-4">
              <h4 className="text-xs font-semibold text-text-tertiary uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <ClockIcon className="w-3.5 h-3.5" />
                Previous Prompts
              </h4>

              {historyLoading ? (
                <div className="flex items-center justify-center py-6">
                  <div className="animate-spin h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full" />
                  <span className="ml-2 text-xs text-text-tertiary">Loading history...</span>
                </div>
              ) : promptHistory && promptHistory.length > 0 ? (
                <div ref={historyRef} className="space-y-2 max-h-[35vh] overflow-y-auto pr-1">
                  {promptHistory.map((entry) => (
                    <div
                      key={entry.id}
                      className="group relative bg-dark-800/50 border border-white/5 rounded-lg p-3 hover:border-primary-500/30 hover:bg-dark-800 transition-all cursor-default"
                      onMouseEnter={(e) => handleEntryHover(entry.id, e)}
                      onMouseLeave={() => { setHoveredEntry(null); setTooltipPos(null); }}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[10px] text-text-muted">{formatDate(entry.created_at)}</span>
                        {isEditable && (
                          <button
                            onClick={() => handleUseHistoryPrompt(entry.prompt_text)}
                            className="text-[10px] px-2.5 py-0.5 rounded bg-primary-500/10 text-primary-400 hover:bg-primary-500/25 opacity-0 group-hover:opacity-100 transition-all font-medium"
                          >
                            Use this
                          </button>
                        )}
                      </div>
                      <p className="text-xs text-text-secondary font-mono line-clamp-2 leading-relaxed">
                        {entry.prompt_text}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-text-muted text-center py-4">No previous prompts found</p>
              )}
            </div>
          )}
        </div>
      </Modal>

      {/* Hover tooltip — rendered via portal-like fixed positioning */}
      {hoveredEntry != null && tooltipPos && hoveredPromptText && (
        <div
          className="fixed z-[100] max-w-md w-[400px] bg-dark-600 border border-primary-500/30 rounded-xl shadow-2xl shadow-black/50 p-4 pointer-events-none"
          style={{
            top: Math.min(tooltipPos.top, window.innerHeight - 320),
            left: Math.min(tooltipPos.left, window.innerWidth - 420),
          }}
        >
          <p className="text-[10px] text-primary-400 font-semibold uppercase tracking-wider mb-2">Full Prompt</p>
          <pre className="whitespace-pre-wrap text-xs text-text-secondary font-mono leading-relaxed max-h-[250px] overflow-y-auto">
            {hoveredPromptText}
          </pre>
        </div>
      )}
    </>
  );
}

export default PromptInfoButton;
