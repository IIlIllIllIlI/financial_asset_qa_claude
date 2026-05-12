"use client";

import { useChatStore } from "@/stores/chatStore";
import { Toaster, toast } from "sonner";
import { useEffect } from "react";

export function ErrorToast() {
  const error = useChatStore((s) => s.error);

  useEffect(() => {
    if (error) {
      toast.error(error.message, {
        description: `错误类型: ${error.type}`,
        duration: 5000,
      });
    }
  }, [error]);

  return <Toaster position="top-right" richColors />;
}
