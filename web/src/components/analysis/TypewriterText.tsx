/**
 * 打字机效果组件
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface TypewriterTextProps {
  text: string;
  speed?: number;
  isStreaming?: boolean;
  onComplete?: () => void;
}

export function TypewriterText({
  text,
  speed = 15,
  isStreaming = false,
  onComplete,
}: TypewriterTextProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [cursorVisible, setCursorVisible] = useState(true);

  // 处理文本显示
  useEffect(() => {
    if (!isStreaming) {
      // 非流式模式：直接显示全部
      setDisplayedText(text);
      return;
    }

    // 流式模式：逐字追赶
    if (text.length <= displayedText.length) {
      return;
    }

    const timeout = setTimeout(() => {
      setDisplayedText(text.slice(0, displayedText.length + 2));
    }, speed);

    return () => clearTimeout(timeout);
  }, [text, displayedText, isStreaming, speed]);

  // 确保显示最新文本（延迟追赶）
  useEffect(() => {
    if (isStreaming && displayedText.length < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => text.slice(0, prev.length + 3));
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [displayedText, text, isStreaming, speed]);

  // 光标闪烁
  useEffect(() => {
    const interval = setInterval(() => {
      setCursorVisible((prev) => !prev);
    }, 530);

    return () => clearInterval(interval);
  }, []);

  // 完成回调
  useEffect(() => {
    if (!isStreaming && displayedText === text && onComplete) {
      onComplete();
    }
  }, [displayedText, text, isStreaming, onComplete]);

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
