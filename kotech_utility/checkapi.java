/*
 * compile: javac -cp '.:apim-gateway-auth-1.1.jar' checkapi.java
 */

import kr.co.smartguru.apim.gateway.util.APIMGatewayUtil;

class checkapi
{
    public static void main (String args[])
    {
	//int checkResult = APIMGatewayUtil.SG_APIM_Check("MAxZkcCcFb68acb-cO6bin0ney-DJLGj5o3offXumcE");
	int checkResult = APIMGatewayUtil.SG_APIM_Check(args[0]);
	System.out.println(checkResult);
    }
}

