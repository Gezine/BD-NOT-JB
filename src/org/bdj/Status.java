package org.bdj;

public class Status {
    private static RemoteLogger LOGGER;
    private static volatile boolean WINDOW = false;

    public static void setScreenOutputEnabled(boolean windowbool) {
        WINDOW = windowbool;
    }

    private static synchronized void initLogger() {
        if (LOGGER == null) {
            LOGGER = new RemoteLogger(18194, 1000);
            LOGGER.start();
            try {
                //Give some time for log client
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    public static void close() {
        synchronized (Status.class) {
            if (LOGGER != null) {
                LOGGER.stop();
                LOGGER = null;
            }
        }
    }

    public static void println(String msg) {
        String finalMsg = "[" + Thread.currentThread().getName() + "] " + msg;
        initLogger();
        LOGGER.println(finalMsg);
        if (WINDOW) {
            Screen.println(finalMsg);
        }
    }

    public static void printStackTrace(String msg, Throwable e) {
        String finalMsg = "[" + Thread.currentThread().getName() + "] " + msg;
        initLogger();
        LOGGER.printStackTrace(finalMsg, e);
        if (WINDOW) {
            Screen.printStackTrace(finalMsg, e);
        }
    }
}