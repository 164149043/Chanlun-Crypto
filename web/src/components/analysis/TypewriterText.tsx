/**
 * 打字机效果组件 - 优化版
 *
 * 优化点：
 * 1. 合并重复的 useEffect 逻辑
 * 2. text 变化时自动重置状态
 * 3. 使用 ref 稳定 onComplete 回调
 * 4. 可配置每次显示字符数
 */

import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';

interface TypewriterTextProps {
  text: string;
  speed?: number;          // 每个字符延迟
  chunkSize?: number;      // 每次显示字符数
  isStreaming?: boolean;
  onComplete?: () => void;
}

export function TypewriterText({
  text,
  speed = 10,
  chunkSize = 3,
  isStreaming = false,
  onComplete,
}: TypewriterTextProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [cursorVisible, setCursorVisible] = useState(true);

  // 用 ref 追踪上一个 text，检测变化
  const prevTextRef = useRef(text);
  const onCompleteRef = useRef(onComplete);

  // 更新 onComplete ref
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  // text 变化时重置（比如切换交易对）
  useEffect(() => {
    if (text !== prevTextRef.current && !text.startsWith(prevTextRef.current)) {
      setDisplayedText('');
      prevTextRef.current = text;
    }
  }, [text]);

  // 流式文本追赶 - 合并逻辑
  useEffect(() => {
    if (!isStreaming) {
      // 非流式模式：直接显示全部
      setDisplayedText(text);
      return;
    }

    // 已追赶完成
    if (displayedText.length >= text.length) {
      return;
    }

    const timeout = setTimeout(() => {
      setDisplayedText((prev) => {
        const nextLength = Math.min(prev.length + chunkSize, text.length);
        return text.slice(0, nextLength);
      });
    }, speed);

    return () => clearTimeout(timeout);
  }, [text, displayedText, isStreaming, speed, chunkSize]);

  // 光标闪烁
  useEffect(() => {
    if (!isStreaming) return;

    const interval = setInterval(() => {
      setCursorVisible((prev) => !prev);
    }, 530);

    return () => clearInterval(interval);
  }, [isStreaming]);

  // 完成回调 - 使用 ref 避免依赖问题
  useEffect(() => {
    if (!isStreaming && displayedText === text && displayedText.length > 0) {
      onCompleteRef.current?.();
    }
  }, [displayedText, text, isStreaming]);

  return (
    <div className="font-mono text-sm leading-relaxed text-slate-200 whitespace-pre-wrap">
      {displayedText}
      {isStreaming && (
        <motion.span
          className="inline-block w-2 h-5 ml-0.5 bg-indigo-400 align-middle"
          animate={{ opacity: cursorVisible ? 1 : 0 }}
          transition={{ duration: 0.1 }}
        />
      )}
    </div>
  );
}
