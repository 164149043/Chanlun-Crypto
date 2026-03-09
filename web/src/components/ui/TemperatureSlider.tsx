/**
 * 温度滑块组件
 * 用于调整 AI 分析的温度参数（0.1 - 1.0）
 */

import { motion } from 'framer-motion';

interface TemperatureSliderProps {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
  color?: string;
  min?: number;
  max?: number;
  step?: number;
}

export function TemperatureSlider({
  value,
  onChange,
  disabled = false,
  color = '#6366f1',
  min = 0.1,
  max = 1.0,
  step = 0.1,
}: TemperatureSliderProps) {
  const percentage = ((value - min) / (max - min)) * 100;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    // 确保值在范围内并保留一位小数
    const clampedValue = Math.max(min, Math.min(max, Math.round(newValue * 10) / 10));
    onChange(clampedValue);
  };

  return (
    <div className={`flex items-center gap-3 ${disabled ? 'opacity-50' : ''}`}>
      <span className="text-xs text-gray-500 w-10">温度</span>
      <div className="relative w-28 h-1.5 bg-gray-200 rounded-full">
        {/* 已滑过的轨道 */}
        <div
          className="absolute h-full rounded-full transition-all duration-150"
          style={{
            width: `${percentage}%`,
            backgroundColor: color,
          }}
        />
        {/* 滑块 */}
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-md border border-gray-200 cursor-pointer"
          style={{ left: `calc(${percentage}% - 8px)` }}
          whileHover={{ scale: disabled ? 1 : 1.2 }}
          whileTap={{ scale: disabled ? 1 : 1.1 }}
        />
        {/* 隐藏的 input */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          disabled={disabled}
          onChange={handleChange}
          className="absolute w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />
      </div>
      <span
        className="text-sm font-medium w-8 text-center"
        style={{ color }}
      >
        {value.toFixed(1)}
      </span>
    </div>
  );
}
