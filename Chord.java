import java.util.*;
import java.net.*;

public class Chord {

    private static Node m_node;
    private static InetSocketAddress m_contact;
    private static Helper m_helper;

    public static void main(String[] args) {
        m_helper = new Helper();
        String local_ip = null;

        try {
            Enumeration<NetworkInterface> nifs = NetworkInterface.getNetworkInterfaces();
            while (nifs.hasMoreElements()){
                NetworkInterface nif = nifs.nextElement();
                Enumeration<InetAddress> address = nif.getInetAddresses();
                while (address.hasMoreElements()){
                    InetAddress addr = address.nextElement();
                    if (addr instanceof Inet4Address){
                        if (addr.getHostAddress().equals("127.0.0.1")){
                            continue;
                        }else{
                            local_ip = "192.168.10.1";
                        }
                    }
                }
            }
//            local_ip = InetAddress.getLocalHost().getHostAddress();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
        System.out.println("Local IP ======:" + local_ip);
        m_node = new Node(Helper.createSocketAddress(local_ip + ":" + args[0]));

        if (args.length == 1) {
            m_contact = m_node.getAddress();
        } else if (args.length == 3) {
            m_contact = Helper.createSocketAddress(args[1] + ":" + args[2]);
            if (m_contact == null) {
                System.out.println("Cannot find address you are trying to contact. Now exit.");
                return;
            }
        } else {
            System.out.println("Wrong input. Exit.");
            System.exit(0);
        }

        boolean successful_join = m_node.join(m_contact);

        if (!successful_join) {
            System.out.println("Cannot connect with the node you are trying to contact. Exit.");
            System.exit(0);
        }
        System.out.println("Local IP :" + local_ip);

        m_node.printNeighbors();

        Scanner userinput = new Scanner(System.in);
        while(true){
            System.out.println("\nType \"info\" to check data or \n type \"quit\"to leave: ");
            String command = null;
            command = userinput.next();
            if (command.startsWith("quit")){
                m_node.stopAllThreads();
                System.out.println("Leaving the ring...");
                System.exit(0);
            }else if (command.startsWith("info")){
                m_node.printDataStructure();
            }
        }


    }

}
