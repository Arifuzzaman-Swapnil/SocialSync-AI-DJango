import { useState } from 'react';
import { InformationCircleIcon, ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/outline';
import { Modal } from './Modal';

interface PromptInfoButtonProps {
  prompt: string;
  label?: string;
  size?: 'sm' | 'md';
}

export function PromptInfoButton({ prompt, label = 'AI Prompt Used', size = 'sm' }: PromptInfoButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!prompt) return null;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center justify-center text-text-tertiary hover:text-accent transition-colors"
        title="View AI prompt used"
      >
        <InformationCircleIcon className={size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'} />
      </button>

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title={label} size="xl">
        <div className="space-y-3">
          <div className="relative">
            <pre className="whitespace-pre-wrap text-sm text-text-secondary bg-dark-800 border border-white/5 rounded-xl p-4 max-h-[60vh] overflow-y-auto font-mono leading-relaxed">
              {prompt}
            </pre>
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 p-1.5 rounded-lg bg-dark-700 hover:bg-dark-600 text-text-tertiary hover:text-text-primary transition-colors"
              title="Copy prompt"
            >
              {copied ? (
                <CheckIcon className="w-4 h-4 text-success" />
              ) : (
                <ClipboardDocumentIcon className="w-4 h-4" />
              )}
            </button>
          </div>
          <p className="text-xs text-text-tertiary">
            This is the exact prompt that was sent to the AI model to generate this content.
          </p>
        </div>
      </Modal>
    </>
  );
}

export default PromptInfoButton;
