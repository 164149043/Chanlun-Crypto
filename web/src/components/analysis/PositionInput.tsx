/**
 * 持仓输入组件
 * 支持选择持仓类型和输入开仓价格
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { useAnalysisStore } from '../../stores/analysisStore';
import type { PositionType } from '../../types/api';

interface PositionInputProps {
  disabled?: boolean;
}

const POSITION_OPTIONS: { value: PositionType; label: string; description: string }[] = [
  { value: 'NONE', label: '无持仓', description: '默认分析模式' },
  { value: 'LONG', label: '做多', description: '持有做多仓位' },
  { value: 'SHORT', label: '做空', description: '持有做空仓位' },
];

export function PositionInput({ disabled = false }: PositionInputProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { position, setPositionType, setEntryPrice } = useAnalysisStore();

  const selectedOption = POSITION_OPTIONS.find((opt) => opt.value === position.type);

  const handleSelectType = (type: PositionType) => {
    setPositionType(type);
    setIsOpen(false);
  };

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value === '') {
      setEntryPrice(null);
    } else {
      const num = parseFloat(value);
      if (!isNaN(num) && num > 0) {
        setEntryPrice(num);
      }
    }
  };

  return (
    <div className="space-y-3">
      {/* 持仓类型选择 */}
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
            <div className="flex items-center gap-2">
              <span>{selectedOption?.label || '选择持仓'}</span>
              {position.type !== 'NONE' && (
                <span className="text-xs text-gray-400">
                  ({selectedOption?.description})
                </span>
              )}
            </div>
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Dropdown Menu */}
          {isOpen && (
            <div className="absolute top-full left-0 mt-2 w-full z-50">
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-lg">
                {POSITION_OPTIONS.map((option) => (
                  <button
                    type="button"
                    key={option.value}
                    onClick={() => handleSelectType(option.value)}
                    className={`
                      w-full px-4 py-2.5 text-left
                      transition-colors duration-150
                      ${option.value === position.type ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'}
                    `}
                  >
                    <div className="font-medium">{option.label}</div>
                    <div className="text-xs text-gray-400">{option.description}</div>
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

      {/* 开仓价格输入（仅在 LONG/SHORT 时显示） */}
      {position.type !== 'NONE' && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2 }}
        >
          <label className="block text-sm text-gray-500 mb-2">开仓均价</label>
          <input
            type="number"
            placeholder="输入开仓均价"
            value={position.entryPrice ?? ''}
            onChange={handlePriceChange}
            disabled={disabled}
            step="0.01"
            min="0"
            className={`
              w-full px-4 py-2.5 rounded-xl
              bg-white border border-gray-200
              text-gray-700 font-medium
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-gray-300'}
            `}
          />
        </motion.div>
      )}
    </div>
  );
}
