/** Custom hooks */

import { useState, useEffect, useRef, useCallback } from 'react';

/** Debounce a value */
export function useDebounce<T>(value: T, delay: number): T {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
        const handler = setTimeout(() => setDebouncedValue(value), delay);
        return () => clearTimeout(handler);
    }, [value, delay]);

    return debouncedValue;
}

/** IntersectionObserver-based infinite scroll trigger */
export function useInfiniteScroll(
    callback: () => void,
    options?: { threshold?: number; enabled?: boolean }
) {
    const sentinelRef = useRef<HTMLDivElement | null>(null);
    const { threshold = 0.1, enabled = true } = options || {};

    useEffect(() => {
        if (!enabled) return;

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0]?.isIntersecting) {
                    callback();
                }
            },
            { threshold }
        );

        const sentinel = sentinelRef.current;
        if (sentinel) {
            observer.observe(sentinel);
        }

        return () => {
            if (sentinel) {
                observer.unobserve(sentinel);
            }
        };
    }, [callback, threshold, enabled]);

    return sentinelRef;
}

/** Scroll to top button visibility */
export function useScrollToTop(threshold = 400) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setVisible(window.scrollY > threshold);
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, [threshold]);

    const scrollToTop = useCallback(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, []);

    return { visible, scrollToTop };
}
