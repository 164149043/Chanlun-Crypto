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
      <span className="text-xs text-gray-500 w-10 shrink-0">温度</span>
      {/* 触摸区域扩大到 44px 方便移动端操作 */}
      <div className="relative flex-1 min-w-[120px] h-11 flex items-center">
        {/* 轨道 */}
        <div className="relative w-full h-2.5 bg-gray-200 rounded-full">
          {/* 已滑过的轨道 */}
          <div
            className="absolute h-full rounded-full transition-all duration-150"
            style={{
              width: `${percentage}%`,
              backgroundColor: color,
            }}
          />
          {/* 滑块 - 24px 大小，移动端友好 */}
          <motion.div
            className="absolute top-1/2 -translate-y-1/2 w-6 h-6 bg-white rounded-full shadow-lg border-2 cursor-pointer"
            style={{
              left: `calc(${percentage}% - 12px)`,
              borderColor: color,
            }}
            whileHover={{ scale: disabled ? 1 : 1.15 }}
            whileTap={{ scale: disabled ? 1 : 0.95 }}
          />
        </div>
        {/* 隐藏的 input - 扩大触摸区域 */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          disabled={disabled}
          onChange={handleChange}
          className="absolute w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed touch-none"
        />
      </div>
      <span
        className="text-sm font-semibold w-10 text-center shrink-0"
        style={{ color }}
      >
        {value.toFixed(1)}
      </span>
    </div>
  );
}
