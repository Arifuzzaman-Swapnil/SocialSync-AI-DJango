import { useState, useEffect } from 'react';
import { InformationCircleIcon, ClipboardDocumentIcon, CheckIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Modal } from './Modal';

interface PromptInfoButtonProps {
  prompt: string;
  label?: string;
  size?: 'sm' | 'md';
  onRegenerate?: (editedPrompt: string) => void | Promise<void>;
  regenerating?: boolean;
  regenerateLabel?: string;
}

export function PromptInfoButton({
  prompt,
  label = 'AI Prompt Used',
  size = 'sm',
  onRegenerate,
  regenerating = false,
  regenerateLabel = 'Regenerate with this prompt',
}: PromptInfoButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [editedPrompt, setEditedPrompt] = useState(prompt);

  // Sync editedPrompt when the source prompt changes (e.g. after regeneration)
  useEffect(() => {
    setEditedPrompt(prompt);
  }, [prompt]);

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

  const isEditable = !!onRegenerate;
  const hasEdits = editedPrompt !== prompt;

  return (
    <>
      <button
        onClick={(e) => { e.stopPropagation(); setIsOpen(true); }}
        className="inline-flex items-center justify-center text-text-tertiary hover:text-accent transition-colors"
        title="View AI prompt used"
      >
        <InformationCircleIcon className={size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'} />
      </button>

      <Modal isOpen={isOpen} onClose={() => { setIsOpen(false); setEditedPrompt(prompt); }} title={label} size="xl">
        <div className="space-y-3">
          {/* Prompt display / editor */}
          <div className="relative">
            {isEditable ? (
              <textarea
                className="w-full text-sm text-text-secondary bg-dark-800 border border-white/5 rounded-xl p-4 max-h-[55vh] min-h-[200px] overflow-y-auto font-mono leading-relaxed resize-y focus:outline-none focus:ring-1 focus:ring-primary-500/50 focus:border-primary-500/30"
                value={editedPrompt}
                onChange={(e) => setEditedPrompt(e.target.value)}
                spellCheck={false}
              />
            ) : (
              <pre className="whitespace-pre-wrap text-sm text-text-secondary bg-dark-800 border border-white/5 rounded-xl p-4 max-h-[60vh] overflow-y-auto font-mono leading-relaxed">
                {prompt}
              </pre>
            )}
          </div>

          {/* Info text */}
          <p className="text-xs text-text-tertiary">
            {isEditable
              ? 'This is the prompt sent to the AI. You can edit it below and regenerate for a different output.'
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
        </div>
      </Modal>
    </>
  );
}

export default PromptInfoButton;
