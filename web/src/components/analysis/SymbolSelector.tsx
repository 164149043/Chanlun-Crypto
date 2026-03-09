/**
 * 币种选择器组件
 * 浅色主题风格
 */

import { ChevronDown } from 'lucide-react';
import { useState } from 'react';
import type { Symbol } from '../../types/api';

interface SymbolSelectorProps {
  value: Symbol;
  onChange: (symbol: Symbol) => void;
  disabled?: boolean;
}

const SYMBOLS: { value: Symbol; label: string }[] = [
  { value: 'BTCUSDT', label: 'BTC/USDT' },
  { value: 'ETHUSDT', label: 'ETH/USDT' },
];

export function SymbolSelector({
  value,
  onChange,
  disabled = false,
}: SymbolSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const selectedSymbol = SYMBOLS.find((s) => s.value === value);

  const handleSelect = (symbol: Symbol) => {
    onChange(symbol);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          flex items-center justify-between gap-2
          px-4 py-2.5 rounded-xl
          bg-white border border-gray-200
          text-gray-700 font-medium
          transition-all duration-200
          w-full
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50 hover:border-gray-300 cursor-pointer'}
        `}
      >
        <span>{selectedSymbol?.label || '选择币种'}</span>
        <ChevronDown
          className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-full z-50">
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-lg">
            {SYMBOLS.map((symbol) => (
              <button
                type="button"
                key={symbol.value}
                onClick={() => handleSelect(symbol.value)}
                className={`
                  w-full px-4 py-2.5 text-left
                  transition-colors duration-150
                  ${symbol.value === value ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'}
                `}
              >
                {symbol.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
