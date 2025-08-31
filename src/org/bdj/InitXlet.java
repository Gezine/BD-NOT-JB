package org.bdj;

import java.awt.BorderLayout;
import javax.tv.xlet.Xlet;
import javax.tv.xlet.XletContext;
import org.havi.ui.HScene;
import org.havi.ui.HSceneFactory;

public class InitXlet implements Xlet {
    private HScene scene;
    private Screen screen;
    private RemoteJarLoader jarLoader;
    private Thread jarLoaderThread;
    private final String jarLoaderThreadName = "JarLoader";
    
    public void initXlet(XletContext context) {
        
        Status.println("BD-J init");
        Status.setScreenOutputEnabled(true);

        screen = Screen.getInstance();
        screen.setSize(1920, 1080);

        scene = HSceneFactory.getInstance().getDefaultHScene();
        scene.add(screen, BorderLayout.CENTER);
        scene.validate();
    }
    
    public void startXlet() {
        screen.setVisible(true);
        scene.setVisible(true);
        
        // Log will be shown on Screen from this point.
        Status.println("Screen initialized");
        
        try {
            jarLoader = new RemoteJarLoader();
            jarLoaderThread = new Thread(jarLoader, jarLoaderThreadName);
            jarLoaderThread.start();
        } catch (Throwable e) {
            Status.printStackTrace("Loader startup failed", e);
        }
        
    }

    public void pauseXlet() {
        screen.setVisible(false);
    }

    public void destroyXlet(boolean unconditional) {
        scene.remove(screen);
        scene = null;
    }
}



